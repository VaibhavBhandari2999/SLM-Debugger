import datetime
import decimal
import ipaddress
import uuid

from django.db import models
from django.template import Context, Template
from django.test import SimpleTestCase
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _


class Suit(models.IntegerChoices):
    DIAMOND = 1, _("Diamond")
    SPADE = 2, _("Spade")
    HEART = 3, _("Heart")
    CLUB = 4, _("Club")


class YearInSchool(models.TextChoices):
    FRESHMAN = "FR", _("Freshman")
    SOPHOMORE = "SO", _("Sophomore")
    JUNIOR = "JR", _("Junior")
    SENIOR = "SR", _("Senior")
    GRADUATE = "GR", _("Graduate")


class Vehicle(models.IntegerChoices):
    CAR = 1, "Carriage"
    TRUCK = 2
    JET_SKI = 3

    __empty__ = _("(Unknown)")


class Gender(models.TextChoices):
    MALE = "M"
    FEMALE = "F"
    NOT_SPECIFIED = "X"

    __empty__ = "(Undeclared)"


class ChoicesTests(SimpleTestCase):
    def test_integerchoices(self):
        """
        Tests the Suit model's integer choices functionality.
        
        This function verifies that the Suit model's choices, labels, values, and names are correctly defined. It also checks the representation of the Suit.DIAMOND constant, its label, value, and the ability to access and convert between constants and their values. The function asserts that Suit is an instance of models.Choices and that Suit.DIAMOND is an instance of Suit with its label and value being instances of Promise and int respectively.
        """

        self.assertEqual(
            Suit.choices, [(1, "Diamond"), (2, "Spade"), (3, "Heart"), (4, "Club")]
        )
        self.assertEqual(Suit.labels, ["Diamond", "Spade", "Heart", "Club"])
        self.assertEqual(Suit.values, [1, 2, 3, 4])
        self.assertEqual(Suit.names, ["DIAMOND", "SPADE", "HEART", "CLUB"])

        self.assertEqual(repr(Suit.DIAMOND), "Suit.DIAMOND")
        self.assertEqual(Suit.DIAMOND.label, "Diamond")
        self.assertEqual(Suit.DIAMOND.value, 1)
        self.assertEqual(Suit["DIAMOND"], Suit.DIAMOND)
        self.assertEqual(Suit(1), Suit.DIAMOND)

        self.assertIsInstance(Suit, type(models.Choices))
        self.assertIsInstance(Suit.DIAMOND, Suit)
        self.assertIsInstance(Suit.DIAMOND.label, Promise)
        self.assertIsInstance(Suit.DIAMOND.value, int)

    def test_integerchoices_auto_label(self):
        """
        Tests the auto-generated labels for integer choices in the Vehicle model.
        
        This function verifies that the auto-generated labels for the integer choices
        in the Vehicle model are correctly set. The Vehicle model uses the `integer_choices`
        method to define its choices, and this function checks that the labels for each
        choice match the expected values:
        
        - CAR: 'Carriage'
        - TRUCK: 'Truck'
        - JET_SKI: 'Jet Ski'
        
        Args:
        """

        self.assertEqual(Vehicle.CAR.label, "Carriage")
        self.assertEqual(Vehicle.TRUCK.label, "Truck")
        self.assertEqual(Vehicle.JET_SKI.label, "Jet Ski")

    def test_integerchoices_empty_label(self):
        """
        Tests the behavior of an integer choices field with an empty label for the Vehicle model.
        
        - Verifies that the first choice tuple is `(None, "(Unknown)")`.
        - Confirms that the first label is `"Unknown"`.
        - Ensures that the first value is `None`.
        - Checks that the first name is `__empty__`.
        
        Args:
        None
        
        Returns:
        None
        """

        self.assertEqual(Vehicle.choices[0], (None, "(Unknown)"))
        self.assertEqual(Vehicle.labels[0], "(Unknown)")
        self.assertIsNone(Vehicle.values[0])
        self.assertEqual(Vehicle.names[0], "__empty__")

    def test_integerchoices_functional_api(self):
        """
        Tests the functionality of the `IntegerChoices` class.
        
        This function verifies that the `IntegerChoices` class correctly initializes with the given choices and returns the expected labels, values, and names.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `models.IntegerChoices`: Creates an instance of `IntegerChoices` with specified choices.
        - `.labels`: Returns the labels of the choices.
        - `.values`: Returns the integer values of the choices.
        """

        Place = models.IntegerChoices("Place", "FIRST SECOND THIRD")
        self.assertEqual(Place.labels, ["First", "Second", "Third"])
        self.assertEqual(Place.values, [1, 2, 3])
        self.assertEqual(Place.names, ["FIRST", "SECOND", "THIRD"])

    def test_integerchoices_containment(self):
        """
        Tests containment of integer choices in the Suit enumeration.
        
        This function checks whether specific values are contained within the Suit enumeration.
        It verifies that the DIAMOND value from the Suit enumeration is present, the integer 1 is present,
        and the integer 0 is not present.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the expected conditions fail.
        """

        self.assertIn(Suit.DIAMOND, Suit)
        self.assertIn(1, Suit)
        self.assertNotIn(0, Suit)

    def test_textchoices(self):
        """
        Tests the YearInSchool choices, labels, values, and names attributes, as well as the representation, label, value, and type of its elements.
        
        This function checks the following:
        - The choices attribute contains the correct list of tuples representing the year in school options.
        - The labels attribute contains the correct list of labels for each option.
        - The values attribute contains the correct list of values for each option.
        - The names attribute contains the correct list of names for each option
        """

        self.assertEqual(
            YearInSchool.choices,
            [
                ("FR", "Freshman"),
                ("SO", "Sophomore"),
                ("JR", "Junior"),
                ("SR", "Senior"),
                ("GR", "Graduate"),
            ],
        )
        self.assertEqual(
            YearInSchool.labels,
            ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"],
        )
        self.assertEqual(YearInSchool.values, ["FR", "SO", "JR", "SR", "GR"])
        self.assertEqual(
            YearInSchool.names,
            ["FRESHMAN", "SOPHOMORE", "JUNIOR", "SENIOR", "GRADUATE"],
        )

        self.assertEqual(repr(YearInSchool.FRESHMAN), "YearInSchool.FRESHMAN")
        self.assertEqual(YearInSchool.FRESHMAN.label, "Freshman")
        self.assertEqual(YearInSchool.FRESHMAN.value, "FR")
        self.assertEqual(YearInSchool["FRESHMAN"], YearInSchool.FRESHMAN)
        self.assertEqual(YearInSchool("FR"), YearInSchool.FRESHMAN)

        self.assertIsInstance(YearInSchool, type(models.Choices))
        self.assertIsInstance(YearInSchool.FRESHMAN, YearInSchool)
        self.assertIsInstance(YearInSchool.FRESHMAN.label, Promise)
        self.assertIsInstance(YearInSchool.FRESHMAN.value, str)

    def test_textchoices_auto_label(self):
        """
        Tests the auto-generated labels for text choices in the Gender enum.
        
        This function verifies that the auto-generated labels for the Gender enum match the expected values:
        - MALE: 'Male'
        - FEMALE: 'Female'
        - NOT_SPECIFIED: 'Not Specified'
        
        Args:
        None
        
        Returns:
        None
        """

        self.assertEqual(Gender.MALE.label, "Male")
        self.assertEqual(Gender.FEMALE.label, "Female")
        self.assertEqual(Gender.NOT_SPECIFIED.label, "Not Specified")

    def test_textchoices_empty_label(self):
        """
        Tests the `choices`, `labels`, `values`, and `names` attributes of the `Gender` model's text choices.
        
        - `choices`: A list of tuples containing the value and label for each choice.
        - `labels`: A list of labels for each choice.
        - `values`: A list of values for each choice.
        - `names`: A list of names for each choice.
        
        Verifies that the first element in each list corresponds to an empty label with a
        """

        self.assertEqual(Gender.choices[0], (None, "(Undeclared)"))
        self.assertEqual(Gender.labels[0], "(Undeclared)")
        self.assertIsNone(Gender.values[0])
        self.assertEqual(Gender.names[0], "__empty__")

    def test_textchoices_functional_api(self):
        """
        Tests the functionality of the `TextChoices` class from Django models.
        
        This function creates an instance of `TextChoices` with the labels 'GOLD', 'SILVER', and 'BRONZE' and checks the following:
        - The labels are correctly set to ['Gold', 'Silver', 'Bronze']
        - The values are correctly set to ['GOLD', 'SILVER', 'BRONZE']
        - The names are correctly set to ['GOLD',
        """

        Medal = models.TextChoices("Medal", "GOLD SILVER BRONZE")
        self.assertEqual(Medal.labels, ["Gold", "Silver", "Bronze"])
        self.assertEqual(Medal.values, ["GOLD", "SILVER", "BRONZE"])
        self.assertEqual(Medal.names, ["GOLD", "SILVER", "BRONZE"])

    def test_textchoices_containment(self):
        """
        Tests containment of YearInSchool values.
        
        This function checks if specific YearInSchool values are contained within the YearInSchool enumeration. It verifies the presence of a full-year designation (FRESHMAN) and an abbreviated designation ("FR") while ensuring that an invalid value ("XX") is not present.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `assertIn`: Verifies that a value is contained within a collection.
        - `YearInSchool
        """

        self.assertIn(YearInSchool.FRESHMAN, YearInSchool)
        self.assertIn("FR", YearInSchool)
        self.assertNotIn("XX", YearInSchool)

    def test_textchoices_blank_value(self):
        """
        Tests the behavior of `models.TextChoices` with a blank value.
        
        This function verifies that when creating a `TextChoices` enum with an empty string as one of the choices,
        the labels, values, and names are correctly set.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `models.TextChoices`: The base class used to define text choices.
        - `labels`: A list of human-readable labels for each choice.
        - `values
        """

        class BlankStr(models.TextChoices):
            EMPTY = "", "(Empty)"
            ONE = "ONE", "One"

        self.assertEqual(BlankStr.labels, ["(Empty)", "One"])
        self.assertEqual(BlankStr.values, ["", "ONE"])
        self.assertEqual(BlankStr.names, ["EMPTY", "ONE"])

    def test_invalid_definition(self):
        """
        Test invalid definitions for IntegerChoices.
        
        - Raises TypeError when a string is used as the second argument in int().
        - Raises ValueError when duplicate values are found in the enum.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `test_invalid_definition`
        - `self.assertRaisesMessage`
        - `models.IntegerChoices`
        
        Important Variables:
        - `msg`: Error message for TypeError or ValueError.
        - `InvalidArgumentEnum`: Enum with invalid argument
        """

        msg = "'str' object cannot be interpreted as an integer"
        with self.assertRaisesMessage(TypeError, msg):

            class InvalidArgumentEnum(models.IntegerChoices):
                # A string is not permitted as the second argument to int().
                ONE = 1, "X", "Invalid"

        msg = "duplicate values found in <enum 'Fruit'>: PINEAPPLE -> APPLE"
        with self.assertRaisesMessage(ValueError, msg):

            class Fruit(models.IntegerChoices):
                APPLE = 1, "Apple"
                PINEAPPLE = 1, "Pineapple"

    def test_str(self):
        """
        Tests the string representation of enum members.
        
        This function iterates over the `Gender`, `Suit`, `YearInSchool`, and `Vehicle` enums,
        and checks that the string representation of each enum member matches the expected value.
        It uses the `subTest` context manager to run individual tests for each member.
        """

        for test in [Gender, Suit, YearInSchool, Vehicle]:
            for member in test:
                with self.subTest(member=member):
                    self.assertEqual(str(test[member.name]), str(member.value))

    def test_templates(self):
        """
        Tests rendering of a template with a context containing a Suit object.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - Template: Used to create the template string.
        - render: Renders the template using the provided context.
        - Context: Creates the context dictionary containing the Suit object.
        
        Variables:
        - template: The template string to be rendered.
        - output: The result of rendering the template.
        - Suit: The object used in the context
        """

        template = Template("{{ Suit.DIAMOND.label }}|{{ Suit.DIAMOND.value }}")
        output = template.render(Context({"Suit": Suit}))
        self.assertEqual(output, "Diamond|1")

    def test_property_names_conflict_with_member_names(self):
        with self.assertRaises(AttributeError):
            models.TextChoices("Properties", "choices labels names values")

    def test_label_member(self):
        """
        Tests the usage of a label as a member in the `Stationery` TextChoices enumeration. Verifies that the label's attributes (label, value, name) are correctly set.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `models.TextChoices`: Used to create an enumeration of stationery types with labels.
        - `self.assertEqual`: Asserts that the label's attributes match the expected values.
        
        Attributes:
        - `Stationery`: An
        """

        # label can be used as a member.
        Stationery = models.TextChoices("Stationery", "label stamp sticker")
        self.assertEqual(Stationery.label.label, "Label")
        self.assertEqual(Stationery.label.value, "label")
        self.assertEqual(Stationery.label.name, "label")

    def test_do_not_call_in_templates_member(self):
        """
        Tests that the `do_not_call_in_templates` member of an IntegerChoices object is correctly initialized and accessible.
        
        - **Important Functions**: `IntegerChoices`, `label`, `value`, `name`
        - **Input Variables**: None
        - **Output Variables**: None
        
        The function creates an IntegerChoices object named `Special` with the label "Do Not Call In Templates". It then verifies that the `do_not_call_in_templates` member has the correct label, value, and
        """

        # do_not_call_in_templates is not implicitly treated as a member.
        Special = models.IntegerChoices("Special", "do_not_call_in_templates")
        self.assertEqual(
            Special.do_not_call_in_templates.label,
            "Do Not Call In Templates",
        )
        self.assertEqual(Special.do_not_call_in_templates.value, 1)
        self.assertEqual(
            Special.do_not_call_in_templates.name,
            "do_not_call_in_templates",
        )


class Separator(bytes, models.Choices):
    FS = b"\x1c", "File Separator"
    GS = b"\x1d", "Group Separator"
    RS = b"\x1e", "Record Separator"
    US = b"\x1f", "Unit Separator"


class Constants(float, models.Choices):
    PI = 3.141592653589793, "π"
    TAU = 6.283185307179586, "τ"


class Set(frozenset, models.Choices):
    A = {1, 2}
    B = {2, 3}
    UNION = A | B
    DIFFERENCE = A - B
    INTERSECTION = A & B


class MoonLandings(datetime.date, models.Choices):
    APOLLO_11 = 1969, 7, 20, "Apollo 11 (Eagle)"
    APOLLO_12 = 1969, 11, 19, "Apollo 12 (Intrepid)"
    APOLLO_14 = 1971, 2, 5, "Apollo 14 (Antares)"
    APOLLO_15 = 1971, 7, 30, "Apollo 15 (Falcon)"
    APOLLO_16 = 1972, 4, 21, "Apollo 16 (Orion)"
    APOLLO_17 = 1972, 12, 11, "Apollo 17 (Challenger)"


class DateAndTime(datetime.datetime, models.Choices):
    A = 2010, 10, 10, 10, 10, 10
    B = 2011, 11, 11, 11, 11, 11
    C = 2012, 12, 12, 12, 12, 12


class MealTimes(datetime.time, models.Choices):
    BREAKFAST = 7, 0
    LUNCH = 13, 0
    DINNER = 18, 30


class Frequency(datetime.timedelta, models.Choices):
    WEEK = 0, 0, 0, 0, 0, 0, 1, "Week"
    DAY = 1, "Day"
    HOUR = 0, 0, 0, 0, 0, 1, "Hour"
    MINUTE = 0, 0, 0, 0, 1, "Hour"
    SECOND = 0, 1, "Second"


class Number(decimal.Decimal, models.Choices):
    E = 2.718281828459045, "e"
    PI = "3.141592653589793", "π"
    TAU = decimal.Decimal("6.283185307179586"), "τ"


class IPv4Address(ipaddress.IPv4Address, models.Choices):
    LOCALHOST = "127.0.0.1", "Localhost"
    GATEWAY = "192.168.0.1", "Gateway"
    BROADCAST = "192.168.0.255", "Broadcast"


class IPv6Address(ipaddress.IPv6Address, models.Choices):
    LOCALHOST = "::1", "Localhost"
    UNSPECIFIED = "::", "Unspecified"


class IPv4Network(ipaddress.IPv4Network, models.Choices):
    LOOPBACK = "127.0.0.0/8", "Loopback"
    LINK_LOCAL = "169.254.0.0/16", "Link-Local"
    PRIVATE_USE_A = "10.0.0.0/8", "Private-Use (Class A)"


class IPv6Network(ipaddress.IPv6Network, models.Choices):
    LOOPBACK = "::1/128", "Loopback"
    UNSPECIFIED = "::/128", "Unspecified"
    UNIQUE_LOCAL = "fc00::/7", "Unique-Local"
    LINK_LOCAL_UNICAST = "fe80::/10", "Link-Local Unicast"


class CustomChoicesTests(SimpleTestCase):
    def test_labels_valid(self):
        """
        Tests that all labels in the specified enumeration classes are valid (i.e., not None).
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any label in an enumeration class is None.
        
        Enumerations Tested:
        - Separator
        - Constants
        - Set
        - MoonLandings
        - DateAndTime
        - MealTimes
        - Frequency
        - Number
        - IPv4Address
        - IPv6Address
        """

        enums = (
            Separator,
            Constants,
            Set,
            MoonLandings,
            DateAndTime,
            MealTimes,
            Frequency,
            Number,
            IPv4Address,
            IPv6Address,
            IPv4Network,
            IPv6Network,
        )
        for choice_enum in enums:
            with self.subTest(choice_enum.__name__):
                self.assertNotIn(None, choice_enum.labels)

    def test_bool_unsupported(self):
        """
        Test that creating a model field with `bool` as a base class raises a TypeError.
        
        This function checks if attempting to create a model field by inheriting from
        both `bool` and `models.Choices` results in a TypeError being raised with
        the specific message: "type 'bool' is not an acceptable base type".
        """

        msg = "type 'bool' is not an acceptable base type"
        with self.assertRaisesMessage(TypeError, msg):

            class Boolean(bool, models.Choices):
                pass

    def test_timezone_unsupported(self):
        """
        Test that creating a model field with an unsupported base type raises a TypeError.
        
        - **Function Name:** `test_timezone_unsupported`
        - **Raises:** `TypeError` with message: "type 'datetime.timezone' is not an acceptable base type"
        - **Class Inheritance:** Inherits from `datetime.timezone` and `models.Choices`.
        - **Expected Behavior:** Attempting to create a class `Timezone` inheriting from both `datetime.timezone` and `models.Choices`
        """

        msg = "type 'datetime.timezone' is not an acceptable base type"
        with self.assertRaisesMessage(TypeError, msg):

            class Timezone(datetime.timezone, models.Choices):
                pass

    def test_uuid_unsupported(self):
        """
        Test that UUID objects are not supported as choices in Django models.
        
        This function checks if attempting to use a UUID object as a choice
        in a Django model raises a TypeError with the message "UUID objects are immutable".
        
        Args:
        None
        
        Raises:
        TypeError: If a UUID object is used as a choice, this error is raised with the specified message.
        
        Example:
        The following code will raise a TypeError:
        
        >>> class Identifier(uuid.UUID, models.Choices):
        """

        msg = "UUID objects are immutable"
        with self.assertRaisesMessage(TypeError, msg):

            class Identifier(uuid.UUID, models.Choices):
                A = "972ce4eb-a95f-4a56-9339-68c208a76f18"
