import django_tables2
from django.utils.translation import gettext_lazy as _

from core.tables.change_logging import ObjectChangeTable
from utilities.tables import register_table_column
from django.db import models


class CustomAccessor(django_tables2.A):
    def resolve(self, context, safe=True, quiet=False):
        """
        Custom logic for resolving data.
        If this accessor is for the `human_summary` column, handle the dynamic logic.
        """
        if self == "human_summary":
            summary = []
            if context.prechange_data and context.postchange_data:
                pre_keys = set(context.prechange_data.keys())
                post_keys = set(context.postchange_data.keys())

                # Added keys
                for key in post_keys - pre_keys:
                    post_value = context.postchange_data[key]
                    summary.append(f"Added {key} = {post_value}")

                # Removed keys
                for key in pre_keys - post_keys:
                    pre_value = context.prechange_data[key]
                    summary.append(f"Removed {key} = {pre_value}")

                # Updated values
                for key in pre_keys & post_keys:
                    if context.prechange_data[key] != context.postchange_data[key]:
                        pre_value = context.prechange_data[key]
                        post_value = context.postchange_data[key]
                        summary.append(f"Updated {key}: {pre_value} → {post_value}")
            return ", ".join(summary) if summary else "No changes detected"

        # Fallback to the default behavior for all other fields
        return super().resolve(context, safe, quiet)


#dummy model and function to use to resolve summary
class ChangeLogSummary(models.Model):

    def get_human_summary():
        return None
    
mycol_2 = ChangeLogSummary.human_summary(
    verbose_name=_('Change Summary'),
    accessor=CustomAccessor('human_summary'),
    default="- -"
)

def register_changelog():
    register_table_column(mycol_2, 'human_summary', ObjectChangeTable)
