# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django_extensions.management.utils import signalcommand
from flex_abac.models import Action, Policy
from flex_abac.constants import SUPERADMIN_ROLE_POLICY


MODEL_NAME = "rolepolicy"
ADMIN_METHODS = ["read", "write"]

class Command(BaseCommand):
    help = "Adds actions related to the rolepolicy model"

    def add_arguments(self, parser):
        pass

    @signalcommand
    def handle(self, *args, **options):

        for method in ADMIN_METHODS:
            policy = Policy.objects.get(name=SUPERADMIN_ROLE_POLICY)
            admin_method, _ = Action.objects.get_or_create(
                name=f"{MODEL_NAME}__{method}",
                pretty_name=f"flex-abac: Allows HTTP {method} method for {MODEL_NAME}"
            )
            policy.actions.add(admin_method)