"""Exercise the standalone notebook's dataset gate without Colab or a GPU."""
import ast
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest


NOTEBOOK = Path(__file__).resolve().parents[1] / 'notebooks/damaged_books_colab.ipynb'


class ColabDatasetGateTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        source = next(''.join(c['source']) for c in self.notebook['cells']
                      if 'def validate_split' in ''.join(c['source']))
        tree = ast.parse(source)
        statements = []
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'uploaded'
                                                    for t in node.targets):
                break
            if isinstance(node, ast.ImportFrom) and node.module == 'google.colab':
                continue
            statements.append(node)
        self.ns = {}
        exec(compile(ast.Module(body=statements, type_ignores=[]), str(NOTEBOOK), 'exec'), self.ns)
        self.ns['EXPECTED_COUNTS'] = dict(train=1, val=1, test=1)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = dict(split_ready=True, classes=list(self.ns['CLASSES']),
                             dataset_version=self.ns['EXPECTED_VERSION'], seed=42,
                             assignment={}, file_sha256={}, quarantined=[])
        for part in ('train', 'val', 'test'):
            image_id = 'image_' + part
            self.manifest['assignment'][part] = [dict(image_id=image_id, group_id='book_' + part)]
            for kind, suffix, content in [('images', '.jpg', part), ('labels', '.txt',
                                          '\n'.join(f'{i} .5 .5 .2 .2' for i in range(5)))]:
                file = self.root / part / kind / (image_id + suffix)
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(content)
                self.manifest['file_sha256'][file.relative_to(self.root).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
        self.save()

    def save(self):
        (self.root / 'split_manifest.json').write_text(json.dumps(self.manifest))

    def validate(self):
        return self.ns['validate_split'](self.root)

    def test_valid_split_and_notebook_code(self):
        self.assertEqual(self.validate()[1]['val']['images'], 1)
        for cell in self.notebook['cells']:
            if cell['cell_type'] == 'code':
                compile(''.join(cell['source']), str(NOTEBOOK), 'exec')
                self.assertEqual(cell['outputs'], [])
        source = '\n'.join(''.join(c['source']) for c in self.notebook['cells'] if c['cell_type'] == 'code')
        tree = ast.parse(source)
        evaluation_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                            and isinstance(n.func, ast.Attribute) and n.func.attr == 'val']
        self.assertEqual(len(evaluation_calls), 1)
        self.assertEqual(next(k.value.value for k in evaluation_calls[0].keywords if k.arg == 'split'), 'val')

    def test_group_leakage_rejected(self):
        self.manifest['assignment']['val'][0]['group_id'] = 'book_train'
        self.save()
        with self.assertRaises(AssertionError): self.validate()

    def test_corrupt_file_rejected(self):
        (self.root / 'train/labels/image_train.txt').write_text('0 .5 .5 .1 .1')
        with self.assertRaises(AssertionError): self.validate()

    def test_wrong_classes_rejected(self):
        self.manifest['classes'][4] = 'Tag'
        self.save()
        with self.assertRaises(AssertionError): self.validate()

    def test_quarantined_image_rejected(self):
        self.manifest['quarantined'] = ['image_val']
        self.save()
        with self.assertRaises(AssertionError): self.validate()

    def test_identical_images_across_splits_rejected(self):
        file = self.root / 'val/images/image_val.jpg'
        file.write_text('train')
        self.manifest['file_sha256']['val/images/image_val.jpg'] = hashlib.sha256(file.read_bytes()).hexdigest()
        self.save()
        with self.assertRaises(AssertionError): self.validate()

    def settings(self):
        source = next(''.join(c['source']) for c in self.notebook['cells']
                      if 'def experiment_settings' in ''.join(c['source']))
        tree = ast.parse(source)
        nodes = [node for node in tree.body if
                 (isinstance(node, ast.FunctionDef) and node.name == 'experiment_settings') or
                 (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'EXPERIMENTS'
                                                       for t in node.targets))]
        namespace = {'re': re}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(NOTEBOOK), 'exec'), namespace)
        return namespace['experiment_settings']

    def test_team_presets_keep_shared_training_rules(self):
        settings = self.settings()
        configs = {}
        for experiment, weights, size in [('n640', 'yolo11n.pt', 640),
                                           ('s640', 'yolo11s.pt', 640),
                                           ('n960', 'yolo11n.pt', 960)]:
            selected, config = settings('member02', experiment, 16)
            self.assertEqual(selected, weights)
            self.assertEqual(config.pop('imgsz'), size)
            configs[experiment] = config
        self.assertEqual(configs['n640'], configs['s640'])
        self.assertEqual(configs['n640'], configs['n960'])
        self.assertEqual(configs['n640']['seed'], 42)

    def test_invalid_team_settings_rejected(self):
        settings = self.settings()
        for args in [('../outside', 'n640', 16), ('', 'n640', 16),
                     ('member', 'unknown', 16), ('member', 'n640', True),
                     ('member', 's640', 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError): settings(*args)
        self.assertEqual(settings('member', 's640', 8)[1]['batch'], 8)

    def test_release_download_and_summary_record_validation_only(self):
        source = '\n'.join(''.join(c['source']) for c in self.notebook['cells'] if c['cell_type'] == 'code')
        self.assertIn('releases/download/', source)
        self.assertIn('damaged-books-reviewed-v1/split-reviewed-v1.zip', source)
        self.assertIn('sha256(temporary) == EXPECTED_SHA256', source)
        tree = ast.parse(source)
        row = next(node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'row' for t in node.targets))
        values = {k.value: v for k,v in zip(row.keys, row.values)}
        self.assertEqual(values['split'].value, 'val')
        self.assertIs(values['test_evaluated'].value, False)


if __name__ == '__main__':
    unittest.main()
