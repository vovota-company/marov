# accounts/migrations/0002_sweeptask_coin_userwallet_fix.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # Add coin field to SweepTask
        migrations.AddField(
            model_name="sweeptask",
            name="coin",
            field=models.CharField(default="", max_length=10),
        ),
    ]
