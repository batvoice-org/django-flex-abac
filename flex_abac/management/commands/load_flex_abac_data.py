from flex_abac.utils.load_flex_abac_data import load_flex_abac_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Loads initial data required to make the permissions system work.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--add_admin_users',
            type=str,
            nargs='+',
            required=False,
            default=[],
            dest="admin_users",
            help="Adds the flex-abac admin role to the provided users."
        )

        parser.add_argument(
            '--add_viewer_users',
            type=str,
            nargs='+',
            required=False,
            default=[],
            dest="viewer_users",
            help="Adds the flex-abac viewer role to the provided users."
        )

        parser.add_argument(
            '--clean_users',
            default=False,
            action='store_true',
            help="Removes flex-abac roles for all users."
        )

    def handle(self, *args, **options):
        load_flex_abac_data(
            admin_users=options["admin_users"],
            viewer_users=options["viewer_users"],
            clean_users=options["clean_users"]
        )

