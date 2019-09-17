"""Test the parsing module."""
import collections
import datetime

from faker import Faker
import pytest

from scrapd.core import parsing
from scrapd.core.constant import Fields
from tests import mock_deceased
from tests import mock_twitter
from tests.test_common import load_test_page
from tests.test_common import TEST_DATA_DIR

# Set faker object.
fake = Faker()


# From https://gist.github.com/angstwad/bf22d1822c38a92ec0a9.
def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k in merge_dct:
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.abc.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


# Represents the expected output when parsing the data from the twitter fields.
# KEEP the keys alphabetically ordered to simplify looking for values manually.
parse_twitter_fields_scenarios = {
    'traffic-fatality-2-3': {
        Fields.CASE: '19-0161105',
        Fields.CRASHES: '2',
    },
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASHES: '71',
        Fields.DATE: datetime.date(2018, 12, 4),
        Fields.LOCATION: '183 service road westbound and Payton Gin Rd.',
        Fields.TIME: datetime.time(20, 39),
    },
    'traffic-fatality-72-1': {
        Fields.CASE: '18-3551763',
        Fields.CRASHES: '72',
        Fields.DATE: datetime.date(2018, 12, 21),
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: datetime.time(20, 20),
    },
    'traffic-fatality-73-2': {
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DATE: datetime.date(2018, 12, 30),
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.NOTES: 'The preliminary investigation shows that a 2003 Ford F150 was '
        'traveling northbound on the US Highway 183 northbound ramp to E. '
        'Highway 71, eastbound. The truck went across the E. Highway 71 and '
        'US Highway 183 ramp, rolled and came to a stop north of the '
        'roadway.',
        Fields.TIME: datetime.time(2, 24),
    },
}

# Represents the expected output when parsing the data from page content.
# KEEP the keys alphabetically ordered to simplify looking for values manually.
parse_page_content_scenarios = {
    'traffic-fatality-2-3': {
        Fields.AGE: 58,
        Fields.CRASHES: '2',
        Fields.DOB: datetime.date(1960, 2, 15),
        Fields.DATE: datetime.date(2019, 1, 16),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Ann',
        Fields.GENDER: 'female',
        Fields.LAST_NAME: 'Bottenfield-Seago',
        Fields.LOCATION: 'West William Cannon Drive and Ridge Oak Road',
        Fields.NOTES: 'The preliminary investigation shows that the grey, 2003 Volkwagen '
        'Jetta being driven by Ann Bottenfield-Seago failed to yield at a '
        'stop sign while attempting to turn westbound on to West William '
        'Cannon Drive from Ridge Oak Road. The Jetta collided with a black, '
        '2017 Chevrolet truck that was eastbound in the inside lane of West '
        'William Cannon Drive. Bottenfield-Seago was pronounced deceased at '
        'the scene. The passenger in the Jetta and the driver of the truck '
        'were both transported to a local hospital with non-life threatening '
        'injuries. No charges are expected to be filed.',
        Fields.TIME: datetime.time(15, 42),
    },
    'traffic-fatality-15-4': {
        Fields.AGE: 27,
        Fields.CASE: '19-0921776',
        Fields.DATE: datetime.date(2019, 4, 2),
        Fields.DOB: datetime.date(1991, 6, 24),
        Fields.ETHNICITY: 'White',
        Fields.CRASHES: '15',
        Fields.FIRST_NAME: 'Garrett',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Davis',
        Fields.LOCATION: '517 E. Slaughter Lane',
        Fields.NOTES: 'The preliminary investigation indicated that Garrett Davis, the '
        'driver of the 2017 Subaru Forester, was traveling eastbound in the '
        '500 block of E. Slaughter Lane when he attempted to turn left and '
        'collided with a 1996 Chevrolet truck that was traveling westbound. '
        'Mr. Davis was attempting to enter the apartment complex on the '
        'south side of the road when he failed to yield right of way. The '
        'truck made contact with the passenger side of the Forester, killing '
        'both the driver and passenger, Keaton Carnley. There were no other '
        'occupants in the Subaru. The driver of the truck suffered minor '
        'injuries. All parties were wearing their seatbelts. No charges are '
        'expected to be filed.',
        Fields.TIME: datetime.time(22, 1)
    },
    'traffic-fatality-20-4': {
        Fields.AGE: 19,
        Fields.CASE: '19-1080319',
        Fields.DATE: datetime.date(2019, 4, 18),
        Fields.CRASHES: '20',
        Fields.ETHNICITY: 'Hispanic',
        Fields.GENDER: 'male',
        Fields.LOCATION: '8000 block of West U.S. 290',
        Fields.TIME: datetime.time(6, 53),
        Fields.NOTES: 'The preliminary investigation revealed that a 2016, black Toyota '
        '4Runner was exiting a private driveway at 8000 W. Hwy. 290. Signs '
        'are posted for right turn only and the driver of the 4Runner failed '
        'to comply and made a left turn. A 2008, gray Ford Mustang was '
        'traveling westbound in the inside lane and attempted to avoid the '
        '4Runner but struck its front end. The Mustang continued into '
        'eastbound lanes of traffic and was struck by a 2013, maroon Dodge '
        'Ram.\n'
        '\n'
        '\tThe driver of the Mustang was pronounced deceased at the scene.',
    },
    'traffic-fatality-50-3': {
        Fields.AGE: 36,
        Fields.CASE: '19-2291933',
        Fields.DATE: datetime.date(2019, 8, 17),
        Fields.ETHNICITY: 'Black',
        Fields.CRASHES: '50',
        Fields.DOB: datetime.date(1982, 12, 28),
        Fields.FIRST_NAME: 'Cedric',
        Fields.GENDER: "male",
        Fields.LAST_NAME: 'Benson',
        Fields.LOCATION: '4500 FM 2222/Mount Bonnell Road',
        Fields.NOTES: 'The preliminary investigation yielded testimony from witnesses who '
        'reported seeing the BMW motorcycle driven by Cedric Benson '
        'traveling at a high rate of speed westbound in the left lane of FM '
        '2222. A white, 2014 Dodge van was stopped at the T-intersection of '
        'Mount Bonnell Road and FM 2222. After checking for oncoming '
        'traffic, the van attempted to turn left on to FM 2222 when it was '
        'struck by the oncoming motorcycle.\n'
        '\n'
        '\tThe driver of the van was evaluated by EMS on scene and refused '
        'transport. The passenger of the van and a bystander at the scene '
        'attempted to render aid to Mr. Benson and his passenger Aamna '
        'Najam. Cedric Benson and Aamna Najam were both pronounced on '
        'scene.\n'
        '\n'
        '\tThe van driver remained on scene and is cooperating with the '
        'ongoing investigation.\n'
        '\n'
        '\tThe family of Cedric Benson respectfully requests privacy during '
        'this difficult time and asks that media refrain from contacting '
        'them.',
        Fields.TIME: datetime.time(22, 20),
    },
    'traffic-fatality-71-2': {
        Fields.AGE: 54,
        Fields.DOB: datetime.date(1964, 6, 1),
        Fields.ETHNICITY: 'Other',
        Fields.FIRST_NAME: 'Barkat',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Umatia',
        Fields.NOTES: 'The preliminary investigation shows that a 2004 Honda sedan was '
        'traveling northbound on Payton Gin Rd. from a stop. A 2006 Mercedes '
        'sedan was traveling westbound on the service road of 183. The '
        'Mercedes and the Honda crashed in the intersection. The Honda was '
        'damaged on the right side and the Mercedes was damaged on the front '
        'end. The driver of the Honda was pronounced deceased at the scene '
        'at 8:50 p.m.',
    },
    'traffic-fatality-72-1': {
        Fields.AGE: 22,
        Fields.DOB: datetime.date(1996, 3, 29),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Elijah',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Perales',
        Fields.NOTES: 'The preliminary investigation shows that the 2016 Indian motorcycle '
        'driven by Elijah Perales was stopped on the right shoulder of N '
        'Mopac SB when an SUV, also traveling southbound, drifted to the '
        'right and struck Perales. Perales was pronounced deceased at the '
        'scene. The driver of the SUV remained on site. Investigators are '
        'still working to determine whether charges will be filed.'
    },
    'traffic-fatality-73-2': {
        Fields.AGE: 38,
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.DATE: datetime.date(2018, 12, 30),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Corbin',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Sabillon-Garcia',
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.TIME: datetime.time(2, 24),
    },
}

# Represents the expected output when parsing the data from both the twitter fields and the page content.
# KEEP the keys alphabetically ordered to simplify looking for values manually.
parse_page_scenarios = {}
dict_merge(parse_page_scenarios, parse_page_content_scenarios)
dict_merge(parse_page_scenarios, parse_twitter_fields_scenarios)


@pytest.mark.parametrize(
    'raw_notes,start,end',
    [
        pytest.param(mock_deceased.DECEASED_WITH_NOTES_00, 'The preliminary', 'be filed.', id='big-paragragh'),
        pytest.param(mock_deceased.DECEASED_WITH_NOTES_01, 'The preliminary', '01:48 a.m.', id='split-paragraphs'),
        pytest.param(
            mock_deceased.DECEASED_WITH_NOTES_02, 'The preliminary', 'be filed.', id='multi-dedeceased-one-paragraphs'),
        pytest.param(
            mock_deceased.DECEASED_WITH_NOTES_03, 'The preliminary', 'contacting them.', id='multi-deceased-fields'),
        pytest.param(
            mock_deceased.DECEASED_WITH_NOTES_04, 'The preliminary', 'Maxima', id='No p tag for Deceased field'),
    ],
)
def test_parse_notes_field(raw_notes, start, end):
    """Ensure notes are parsed correctly."""
    soup = parsing.to_soup(raw_notes)
    deceased_field_list = parsing.parse_deceased_field(soup)
    notes = parsing.parse_notes_field(soup, deceased_field_list[-1])
    assert notes.startswith(start)
    assert notes.endswith(end)


# @pytest.mark.parametrize(
#     'raw_deceased,start,end',
#     [
#         pytest.param(mock_deceased.DECEASED_00, 'Garre', '13/1991'),
#         pytest.param(mock_deceased.DECEASED_01, 'Cedric', '01/26/1992'),
#     ],
# )
# def test_parse_deceased_field_00(raw_deceased, start, end):
#     """Ensure the deceased fields is parse correctly."""
#     deceased_soup = parsing.to_soup(raw_deceased)
#     deceased = parsing.parse_deceased_field(deceased_soup)
#     assert deceased[0].startswith(start)
#     assert deceased[-1].endswith(end)


@pytest.mark.parametrize(
    'input_,expected',
    [
        pytest.param(
            '<p>	<strong>Deceased: </strong> Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994</p>',
            ['Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994'],
            id="p, strong, pipes",
        ),
        pytest.param(
            '<p>	<strong>Deceased: </strong> Cecil Wade Walker, White male, D.O.B. 3-7-70</p>',
            ['Cecil Wade Walker, White male, D.O.B. 3-7-70'],
            id="p, strong, commas",
        ),
        pytest.param(
            '<p style="margin-left:.25in;">'
            '<strong>Deceased:&nbsp;</strong> Halbert Glen Hendricks | Black male | 9-24-78</p>',
            ['Halbert Glen Hendricks | Black male | 9-24-78'],
            id="p with style, strong, pipes",
        ),
        pytest.param(
            '',
            [],
            id="Deceased tag not found",
        ),
        pytest.param(
            '<p>	<strong>Deceased:&nbsp; </strong>Hispanic male, 19 years of age<br>',
            ['Hispanic male, 19 years of age'],
            id='XX years of age of age format + included in notes paragraph',
        ),
        pytest.param(
            '<p>	<strong><span style="font-family: &quot;Verdana&quot;,sans-serif;">Deceased:</span></strong>&nbsp; '
            '&nbsp;Ann Bottenfield-Seago, White female, DOB 02/15/1960<br>',
            ['Ann Bottenfield-Seago, White female, DOB 02/15/1960'],
            id='included in notes paragraph',
        ),
        pytest.param(
            '<p>	<strong>Deceased:   </strong>David John Medrano,<strong> </strong>Hispanic male, D.O.B. 6-9-70</p>',
            ['David John Medrano, Hispanic male, D.O.B. 6-9-70'],
            id='stray strong in the middle',
        ),
        pytest.param(
            '<p>	<strong>Deceased 1:&nbsp; </strong>Cedric Benson | Black male | 12/28/1982</p>'
            '<p>	<strong>Deceased 2:&nbsp; </strong>Aamna Najam | Asian female | 01/26/1992</p>',
            ['Cedric Benson | Black male | 12/28/1982', 'Aamna Najam | Asian female | 01/26/1992'],
            id='double deceased',
        ),
        pytest.param(
            '<p> <strong>Deceased:   </strong>Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977) </p>',
            ['Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977)'],
            id='colon after DOB',
        ),
        pytest.param(
            '<strong>Deceased:  </strong>Garrett Evan Davis | White male | 06/24/1991<br>'
            'Keaton Michael Carnley | White male | 11/13/1991                  <br>',
            [],
            id="Multiple fatalities",
            marks=pytest.mark.xfail(reason="Does not know how to handle this case yet."),
        ),
        pytest.param(
            '<p>	<strong>Deceased 1:  </strong>Cedric Benson | Black male | 12/28/1982</p>'
            '<p>	<strong>Deceased 2:  </strong>Aamna Najam | Asian female | 01/26/1992</p',
            [],
            id="Multiple fatalities - other format",
            marks=pytest.mark.xfail(reason="Does not know how to handle this case yet."),
        ),
    ],
)
def test_parse_deceased_field_00(input_, expected):
    """Ensure the deceased field gets parsed correctly."""
    field = parsing.to_soup(input_)
    deceased_str = parsing.parse_deceased_field(field)
    assert deceased_str == expected


@pytest.mark.parametrize('input_,expected', (
    ({
        'Time': 345
    }, {
        'Time': 345
    }),
    ({
        'Time': ['123', '345']
    }, {
        'Time': '123 345'
    }),
    ({
        'Time': ' '
    }, {}),
    ({
        'Time': None
    }, {}),
))
def test_sanitize_fatality_entity(input_, expected):
    """Ensure field values are sanitized."""
    actual = parsing.sanitize_fatality_entity(input_)
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
class TestPageParse:
    """Group the test cases for the `parsing.parse_page` function."""

    def test_parse_page_00(self, filename, expected):
        """Ensure location information is properly extracted from the page."""
        page = load_test_page(filename)
        actual = parsing.parse_page(page, fake.uri())
        assert next(actual) == expected

    @pytest.mark.skip(reason="This should be tested by test_parse_page_00")
    def test_multiple_deceased(self, filename, expected):
        """Ensure multiple deceased are parsed correctly."""
        page_text = load_test_page(filename)
        content_parser = parsing.parse_page(page_text, 'fake_url')
        _ = next(content_parser)
        second = next(content_parser)
        for key in expected:
            assert second[key] == expected[key]

    def test_parse_page_with_missing_data(self, filename, expected):
        """Ensure a page with missing data raises an exception."""
        records = parsing.parse_page("Case:    19-1234567", fake.uri())
        with pytest.raises(StopIteration):
            next(records)

    @pytest.mark.skip(reason="Why location only? -- Duplicate of test_parse_page_00")
    def test_parse_page_get_location(self, filename, expected):
        """Ensure location information is properly extracted from the page."""
        page_fd = TEST_DATA_DIR / filename
        page = page_fd.read_text()
        actual = parsing.parse_page(page, fake.uri())
        assert next(actual) == expected

    @pytest.mark.skip(reason="Irrelevant because test_parse_page_00 tests the same thing")
    def test_parse_page_01(self, filename, expected):
        """Ensure information are properly extracted from the page.
        Don't compare notes if parsed from details page."""
        page_fd = TEST_DATA_DIR / filename
        page = page_fd.read_text()
        actual = next(parsing.parse_page(page, fake.uri()))
        if Fields.NOTES in actual and Fields.NOTES not in expected:
            del actual[Fields.NOTES]
        assert actual == expected

    @pytest.mark.skip(reason="Irrelevant because test_parse_page_00 tests the same thing")
    def test_parse_page_02(self, mocker, filename, expected):
        """Ensure ."""
        data = {}
        parsing_errors = ['one error']
        page_fd = TEST_DATA_DIR / filename
        page = page_fd.read_text()
        pc = mocker.patch('scrapd.core.parsing.parse_page_content', return_value=(data, parsing_errors))
        _ = parsing.parse_page(page, fake.uri())
        assert pc.called_once

    @pytest.mark.skip(reason="Irrelevant because test_parse_page_00 tests the same thing")
    def test_parse_page_02(self, filename, expected):
        """Ensure information are properly extracted from the content detail page.
            Don't compare notes if parsed from details page."""
        page_fd = TEST_DATA_DIR / filename
        page = page_fd.read_text()
        actual = next(parsing.parse_page(page, 'fake_url'))
        if Fields.NOTES in actual and Fields.NOTES not in expected:
            del actual[Fields.NOTES]
        if Fields.DECEASED in actual and Fields.DECEASED not in expected:
            del actual[Fields.DECEASED]
        assert actual == expected


class TestPageParseContent:
    """Group the test cases for the `parsing.parse_page_content` function."""

    # @pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_content_scenarios.items()])
    # def test_parse_page_content_03(self, filename, expected):
    #     """Ensure location information is properly extracted from the page."""
    #     page = load_test_page(filename)
    #     actual = parsing.parse_page_content(page, fake.uri())
    #     assert next(actual) == expected

    def test_parse_page_content_00(self, mocker):
        """Ensure a `process_deceased_field` exception is caught and does not propagate."""
        page_fd = TEST_DATA_DIR / 'traffic-fatality-2-3'
        page = page_fd.read_text()
        # Why did we patch an unused function???
        mocker.patch('scrapd.core.person.process_deceased_field', side_effect=ValueError)
        result, _ = parsing.parse_page_content(page)
        if Fields.DECEASED in result:
            del result[Fields.DECEASED]
        assert len(result) == 6

    def test_parse_page_content_01(self):
        """Ensure a log entry is created if there is no deceased field.
        THIS IS NOT WHAT THE TEST DOES."""
        result, _ = parsing.parse_page_content('Case: 01-2345678')
        assert result

    def test_parse_page_content_02(self):
        """Ensure a missing case number raises an exception."""
        with pytest.raises(ValueError):
            parsing.parse_page_content('There is no case number here.')


class TestParseTwitter:
    """Group the test cases for parsing the Twitter data."""

    @pytest.mark.parametrize('input_,expected', (
        (mock_twitter.title_00, {
            Fields.CRASHES: '73'
        }),
        (None, {}),
    ))
    def test_parse_twitter_title_00(self, input_, expected):
        """Ensure the Twitter title gets parsed correct."""
        actual = parsing.parse_twitter_title(input_)
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    @pytest.mark.parametrize('input_,expected', (
        (
            mock_twitter.description_00,
            {
                'Case': '18-3640187',
                'Date': datetime.date(2018, 12, 30),
                'DOB': datetime.date(1980, 2, 9),
                'Time': datetime.time(2, 24),
                'Location': '1400 E. Highway 71 eastbound',
                'Notes': 'The preliminary investigation shows that a 2003 Ford F150 was '
                'traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. '
                'The truck went across the E. Highway 71 and US Highway 183 ramp, rolled '
                'and came to a stop north of the roadway.',
                'Deceased': ['Corbin Sabillon-Garcia, White male,']
            },
        ),
        (None, {}),
    ))
    def test_parse_twitter_description_00(self, input_, expected):
        """Ensure the Twitter description gets parsed correctly."""
        actual = parsing.parse_twitter_description(input_)
        assert actual == expected

    @pytest.mark.parametrize('input_,expected', [
        pytest.param(
            mock_twitter.description_01,
            {Fields.CASE: '19-0161105'},
            id="Case number only",
        )
    ])
    def test_parse_twitter_description_10(self, input_, expected):
        """Ensure the Twitter description gets parsed correctly."""
        actual = parsing.parse_twitter_description(input_)
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    def test_parse_twitter_description_01(self, ):
        """Ensure the Twitter description gets parsed correctly."""
        actual = parsing.parse_twitter_description(mock_twitter.description_01)
        expected = {
            Fields.CASE: '19-0161105',
        }
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    def test_parse_twitter_description_02(self, ):
        """Ensure a DOB recognized as a field can be parsed."""
        actual = parsing.parse_twitter_description(mock_twitter.description_02)
        expected = {
            Fields.CASE: '18-160882',
            Fields.DOB: datetime.date(1961, 1, 22),
            Fields.DATE: datetime.date(2018, 1, 16),
            Fields.LOCATION: '1500 W. Slaughter Lane',
            Fields.TIME: datetime.time(17, 14),
        }
        if Fields.DECEASED in actual:
            del actual[Fields.DECEASED]
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    def test_parse_twitter_description_03(self):
        """Ensure a DOB recognized as a field can be parsed."""
        actual = parsing.parse_twitter_description(mock_twitter.description_03)
        expected = {}
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    def test_parse_twitter_description_without_notes(self):
        """
        Test that the parser finds the right number of deceased people.
        """
        twitter_description = ("'Case:         19-1321936 Date:          May 12, 2019 "
                               "Time:         11:34 p.m. Location:   12100 N. IH-35 NB Service road "
                               "Deceased:  First Middle Last, Black male, D.O.B. August 30, 1966'")
        d = parsing.parse_twitter_description(twitter_description)
        assert not d.get("D.O.B.")
        assert d[Fields.DOB] == datetime.date(1966, 8, 30)

    @pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_twitter_fields_scenarios.items()])
    def test_parse_twitter_fields_00(self, filename, expected):
        """Ensure information are properly extracted from the twitter fields on detail page."""
        page = load_test_page(filename)
        actual = parsing.parse_twitter_fields(page)
        if Fields.DECEASED in actual and Fields.DECEASED not in expected:
            del actual[Fields.DECEASED]
        assert actual == expected

    @pytest.mark.skip(reason="Useless")
    @pytest.mark.parametrize(
        'raw_deceased,start,end',
        [
            pytest.param(
                mock_twitter.description_04,
                'Cedric',
                '01/26/1992',
                marks=pytest.mark.xfail(reason="need more info"),
            ),
        ],
    )
    def test_parse_twitter_fields_01(self, raw_deceased, start, end):
        # page_text = load_test_page(page)
        # parsed_content = parsing.parse_twitter_fields(page_text)
        # deceased = parsed_content[Fields.DECEASED]
        deceased = parsing.twitter_deceased_field_to_list(raw_deceased)
        assert deceased[0].startswith(start)
        assert deceased[-1].endswith(end)
