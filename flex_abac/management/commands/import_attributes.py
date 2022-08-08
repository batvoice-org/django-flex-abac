from flex_abac.utils.import_attributes import import_from_yaml
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Imports attributes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yaml-path',
            type=str,
            required=True,
            dest="yaml_path",
            help="Path to yaml containing data to load"
        )

    def handle(self, *args, **options):
        import_from_yaml(options['yaml_path'])



if __name__=="__main__":
    PATH = "./attributes_example_simple.yaml"
    import_from_yaml(PATH)