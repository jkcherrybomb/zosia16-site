from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from conferences.models import Bus, Zosia
from utils.test_helpers import create_bus, create_user, create_user_preferences, create_zosia
from utils.time_manager import now, time_point

User = get_user_model()


class ZosiaTestCase(TestCase):
    def setUp(self):
        self.normal = create_user(0)
        self.active = create_zosia(active=True)

    def test_only_one_active_Zosia_can_exist(self):
        """Creating another active Zosia throws an error"""
        with self.assertRaises(ValidationError):
            create_zosia(active=True, commit=False).full_clean()

    def test_find_active(self):
        """Zosia.find_active returns active Zosia"""
        self.assertEqual(self.active.pk, Zosia.objects.find_active().pk)

    def test_end_date(self):
        """Zosia has 4 days"""
        self.assertEqual(self.active.end_date, self.active.start_date + timedelta(days=3))

    def test_can_user_choose_room_when_at_user_start_time(self):
        self.active.rooming_start = now()
        self.active.save()
        user_prefs = create_user_preferences(self.normal, self.active, payment_accepted=True,
                                             bonus_minutes=0)

        result = self.active.can_user_choose_room(user_prefs)

        self.assertTrue(result)

    def test_can_user_choose_room_when_before_user_start_time(self):
        self.active.rooming_start = time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(self.normal, self.active, payment_accepted=True,
                                             bonus_minutes=1)

        result = self.active.can_user_choose_room(user_prefs, time=time_point(2016, 12, 22, 23, 58))
        self.assertFalse(result)

    def test_can_user_choose_room_when_after_user_start_time(self):
        self.active.rooming_start = time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(self.normal, self.active, payment_accepted=True,
                                             bonus_minutes=3)

        result = self.active.can_user_choose_room(user_prefs, time=time_point(2016, 12, 22, 23, 58))
        self.assertTrue(result)


class BusTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = create_user(0)
        self.zosia = create_zosia()

        self.bus1 = create_bus(zosia=self.zosia, capacity=0)
        self.bus2 = create_bus(zosia=self.zosia, capacity=1)
        self.bus3 = create_bus(zosia=self.zosia, capacity=2)

    def test_find_buses_with_free_places_when_all_empty(self):
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 2)

    def test_find_buses_with_free_places_when_bus_chosen_and_full(self):
        create_user_preferences(self.normal, self.zosia, bus=self.bus2)
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 1)

    def test_find_buses_with_free_places_when_bus_chosen_and_not_full(self):
        create_user_preferences(self.normal, self.zosia, bus=self.bus3)
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 2)

    def test_find_available_when_all_empty(self):
        buses = Bus.objects.find_available(self.zosia)
        self.assertEqual(buses.count(), 2)

    def test_find_available_when_bus_chosen_and_full(self):
        create_user_preferences(self.normal, self.zosia, bus=self.bus2)
        buses = Bus.objects.find_available(self.zosia)
        self.assertEqual(buses.count(), 1)

    def test_find_available_when_bus_chosen_and_not_full(self):
        create_user_preferences(self.normal, self.zosia, bus=self.bus3)
        buses = Bus.objects.find_available(self.zosia)
        self.assertEqual(buses.count(), 2)

    def test_find_available_when_passenger_and_bus_chosen_and_full(self):
        user_prefs = create_user_preferences(self.normal, self.zosia, bus=self.bus2)
        buses = Bus.objects.find_available(self.zosia, passenger=user_prefs)
        self.assertEqual(buses.count(), 2)

    def test_find_available_when_passenger_and_bus_chosen_and_not_full(self):
        user_prefs = create_user_preferences(self.normal, self.zosia, bus=self.bus3)
        buses = Bus.objects.find_available(self.zosia, passenger=user_prefs)
        self.assertEqual(buses.count(), 2)
