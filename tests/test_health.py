import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.health.models import Medicine, MedicineLog, WellnessTip, HydrationLog
from apps.health.views import get_wellness_card_context

class HealthModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='health_user', email='health@test.com', password='password123')
        WellnessTip.objects.create(
            title='Test Hydration Tip',
            tip_text='Drink water to feel good.',
            category='HYDRATION',
            is_active=True
        )

    def test_medicine_creation_and_scheduled_times(self):
        med = Medicine.objects.create(
            user=self.user,
            name='Vitamin D3',
            dosage='1000 IU',
            frequency='TWICE',
            scheduled_times=['08:00', '20:00'],
            start_date=timezone.localdate(),
            notes='Take with breakfast and dinner'
        )
        self.assertTrue(med.is_currently_active())
        self.assertEqual(len(med.scheduled_times), 2)
        self.assertIn("08:00", med.get_times_display())

    def test_adherence_log_calculation(self):
        med = Medicine.objects.create(
            user=self.user,
            name='Omega 3',
            dosage='500mg',
            frequency='ONCE',
            scheduled_times=['09:00']
        )
        today = timezone.localdate()
        
        # Log 6 taken doses and 1 skipped dose over the past 7 days
        for i in range(6):
            d = today - datetime.timedelta(days=i)
            MedicineLog.objects.create(
                medicine=med,
                user=self.user,
                scheduled_date=d,
                scheduled_time='09:00',
                status='TAKEN'
            )
        
        MedicineLog.objects.create(
            medicine=med,
            user=self.user,
            scheduled_date=today - datetime.timedelta(days=6),
            scheduled_time='09:00',
            status='SKIPPED'
        )

        context = get_wellness_card_context(self.user)
        self.assertEqual(context['taken_doses'], 6)
        self.assertEqual(context['total_logged_doses'], 7)
        self.assertEqual(context['adherence_rate'], int(6/7 * 100)) # ~85%
        self.assertIn("You've taken 6 of 7 doses this week", context['adherence_summary'])

    def test_daily_water_intake_tracking_and_reset(self):
        profile = self.user.profile
        profile.water_intake_today = 5
        profile.last_water_reset_date = timezone.localdate() - datetime.timedelta(days=1)
        profile.save()

        # Check that check_and_reset_daily_water resets count on new day
        profile.check_and_reset_daily_water()
        profile.refresh_from_db()
        self.assertEqual(profile.water_intake_today, 0)
        self.assertEqual(profile.last_water_reset_date, timezone.localdate())

    def test_who_water_calculations_by_age(self):
        profile = self.user.profile
        
        # Test Adult Male (Age 28, 70kg, Desk job)
        profile.age = 28
        profile.gender = 'M'
        profile.weight_kg = 70.0
        profile.activity_level = 'SEDENTARY'
        profile.save()

        glasses, liters, expl = profile.calculate_who_recommended_water_glasses()
        self.assertGreaterEqual(glasses, 10)
        self.assertGreaterEqual(liters, 2.5)
        self.assertIn("WHO guideline for Age 28", expl)

        # Test Adaptive Interval for 9-hour work day (09:00 - 18:00)
        profile.water_daily_target = 10
        profile.active_hours_start = datetime.time(9, 0)
        profile.active_hours_end = datetime.time(18, 0)
        interval = profile.calculate_adaptive_hydration_interval_minutes()
        # 540 mins / 10 glasses = 54 mins
        self.assertEqual(interval, 54)
