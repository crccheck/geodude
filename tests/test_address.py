from utils.address import clean_zipcode, clean_street


def test_clean_zipcode_works():
    fixtures = (
        ('', ''),
        ('12345', '12345'),
        ('12345-1234', '12345'),
        ('123456789', '12345'),
        ('12345678a', '12345678a'),
        ('123456789a', '123456789a'),
    )
    for input, expected in fixtures:
        assert clean_zipcode(input) == expected


def test_clean_street_concatenation_works():
    fixtures = (
        ('123 Fake Street', '', '123 Fake ST'),
        (' 123 Fake Street ', ' ', '123 Fake ST'),
    )
    for addr1, addr2, expected in fixtures:
        assert clean_street(addr1, addr2) == expected


def test_clean_street_works():
    fixtures = (
        ('1001 Congress Avenue Suite 450', '1001 Congress AVE STE 450'),
        ('1001 Congress Ste 200', '1001 Congress STE 200'),
        ('1001 G Street NW #400-E', '1001 G ST NW # 400-E'),
        ('1001 Pennsylvania Ave NW Suite 710', '1001 Pennsylvania AVE NW STE 710'),
        ('1005 Congress Ave Ste 1000B', '1005 Congress AVE STE 1000B'),
        ('101 East Gillis PO Box 677', '101 E Gillis PO Box 677'),
        ('101 Parklane Boulevard Suite 301', '101 Parklane BLVD STE 301'),
        ('901 E Street NW 10th Floor', '901 E ST NW 10th FL'),
        ('1000 Louisiana ST. STE 5600', '1000 Louisiana ST STE 5600'),
        ('1000 S. Beckham', '1000 S Beckham'),
        ('P O Box 7230', 'PO Box 7230'),
    )
    for addr1, expected in fixtures:
        assert clean_street(addr1) == expected


def test_clean_street_can_pass_in_zipcode():
    fixtures = (
        ('P O Box 7230', '12345', 'PO Box 7230'),
        ('P O Box 7230', 'gibberish', 'PO Box 7230'),  # XXX
    )
    for addr1, zipcode, expected in fixtures:
        assert clean_street(addr1, zipcode=zipcode) == expected


def test_clean_street_handles_care_of():
    fixtures = (
        ('', '', ''),
        ('c/o Dude', 'PO Box 123', 'PO Box 123'),
        ('C/O Dude', 'PO Box 123', 'PO Box 123'),
    )
    for addr1, addr2, expected in fixtures:
        assert clean_street(addr1, addr2) == expected


def test_clean_street_strips_occupancy():
    fixtures = (
        ('1001 Congress Avenue Suite 450', '1001 Congress AVE'),
        ('1001 Congress Ste 200', '1001 Congress'),
        ('1001 G Street NW #400-E', '1001 G ST NW'),
        ('1001 Pennsylvania Ave NW Suite 710', '1001 Pennsylvania AVE NW'),
        ('1005 Congress Ave Ste 1000B', '1005 Congress AVE'),
        ('101 East Gillis PO Box 677', '101 E Gillis PO Box 677'),
        ('101 Parklane Boulevard Suite 301', '101 Parklane BLVD'),
        ('901 E Street NW 10th Floor', '901 E ST NW'),
        ('1000 Louisiana ST. STE 5600', '1000 Louisiana ST'),
        ('1000 S. Beckham', '1000 S Beckham'),
        ('P O Box 7230', 'PO Box 7230'),
    )
    for addr1, expected in fixtures:
        assert clean_street(addr1, strip_occupancy=True) == expected
