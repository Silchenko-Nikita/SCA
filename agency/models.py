from django.db import models

COMPLETE_STATE_CHOICES = (
    ('NS', 'Not Started'),
    ('IP', 'In Progress'),
    ('C', 'Completed'),
)


class SpyCat(models.Model):
    name = models.CharField(verbose_name="Name", max_length=64)
    years_of_experience = models.IntegerField(verbose_name="Years of Experience")
    breed = models.CharField(verbose_name="Breed", max_length=128)
    salary = models.DecimalField(verbose_name="Salary", max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'spy_cat'
        verbose_name = 'Spy Cat'
        verbose_name_plural = 'Spy Cats'


class Mission(models.Model):
    spy_cat = models.OneToOneField(SpyCat, verbose_name="Cat", related_name="current_mission",
                                   on_delete=models.SET_NULL, null=True, blank=True)
    complete_state = models.CharField(verbose_name="Complete State",
                                      max_length=2, choices=COMPLETE_STATE_CHOICES, default='NS')

    class Meta:
        db_table = 'mission'
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'


class Target(models.Model):
    mission = models.ForeignKey(Mission, verbose_name="Mission", related_name='targets', on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Name", max_length=128)
    country = models.CharField(verbose_name="Country", max_length=255)
    complete_state = models.CharField(verbose_name="Complete State",
                                      max_length=2, choices=COMPLETE_STATE_CHOICES, default='NS')

    class Meta:
        db_table = 'target'
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.complete_state == 'C':
            all_mission_targets_completed = all(
                target.complete_state == 'C' for target in self.mission.targets.all()
            )
            if all_mission_targets_completed:
                self.mission.complete_state = 'C'
                self.mission.save()


class Note(models.Model):
    target = models.ForeignKey(Target, verbose_name="Targets", related_name='notes', on_delete=models.CASCADE)
    text = models.CharField(verbose_name="Text", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'note'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
