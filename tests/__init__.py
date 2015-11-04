import os

from vcr import VCR


fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')

vcr = VCR(
    cassette_library_dir=fixtures,
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_post_data_parameters=['password'],
)
