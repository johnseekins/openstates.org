import pytest
from people_admin.models import UnmatchedName, NameStatus
from people_admin.utils import check_sponsorships, check_votes, update_unmatched
from testutils.factories import create_test_bill, create_test_vote


@pytest.mark.django_db
def test_check_sponsorships(django_assert_num_queries, kansas):
    # create two bills for the sponsor
    create_test_bill("2020", "upper")
    create_test_bill("2020", "upper", sponsors=1)
    create_test_bill("2020", "upper", sponsors=1)
    session = kansas.legislative_sessions.get(identifier="2020")

    with django_assert_num_queries(1):
        missing = check_sponsorships(session)
        assert missing == {"Someone": 2}


@pytest.mark.django_db
def test_check_votes(django_assert_num_queries, kansas):
    b = create_test_bill("2020", "upper")
    create_test_vote(b)
    create_test_vote(b, yes_votes=["A", "Someone"], no_votes=["C"])
    b2 = create_test_bill("2020", "upper")
    create_test_vote(b2, no_votes=["A", "C"])

    session = kansas.legislative_sessions.get(identifier="2020")

    with django_assert_num_queries(1):
        missing = check_votes(session)
        assert missing == {"A": 2, "Someone": 1, "C": 2}


@pytest.mark.django_db
def test_update_unmatched(django_assert_num_queries, kansas):
    b = create_test_bill("2020", "upper", sponsors=1)
    create_test_vote(b, yes_votes=["Someone"], no_votes=["Someone Else"])
    # Someone will have 1 vote and 1 sponsorship
    # Someone Else will have 1 vote

    update_unmatched("ks", "2020")

    unmatched = UnmatchedName.objects.all().order_by("name")
    assert len(unmatched) == 2
    assert unmatched[0].name == "Someone"
    assert unmatched[0].sponsorships_count == 1
    assert unmatched[0].votes_count == 1
    assert unmatched[1].name == "Someone Else"
    assert unmatched[1].sponsorships_count == 0
    assert unmatched[1].votes_count == 1
    assert unmatched[0].status == NameStatus.UNMATCHED


@pytest.mark.django_db
def test_update_unmatched_idempotent(django_assert_num_queries, kansas):
    # will create Someone & Someone Else
    b = create_test_bill("2020", "upper", sponsors=1)
    create_test_vote(b, yes_votes=["Someone"], no_votes=["Someone Else"])
    update_unmatched("ks", "2020")

    # set statuses
    unmatched = list(UnmatchedName.objects.all().order_by("name"))
    unmatched[0].status = NameStatus.IGNORED
    unmatched[0].save()
    unmatched[1].status = NameStatus.SOURCE_ERROR
    unmatched[1].save()
    assert UnmatchedName.objects.count() == 2

    # call it again
    update_unmatched("ks", "2020")
    unmatched = UnmatchedName.objects.all().order_by("name")
    assert len(unmatched) == 2
    assert unmatched[0].status == NameStatus.IGNORED
    assert unmatched[1].status == NameStatus.SOURCE_ERROR


@pytest.mark.django_db
def test_update_unmatched_removes_matched(django_assert_num_queries, kansas):
    # will create Someone & Someone Else
    b = create_test_bill("2020", "upper", sponsors=1)
    create_test_vote(b, yes_votes=["Someone"], no_votes=["Someone Else"])
    update_unmatched("ks", "2020")

    # drop the vote, which will remove Someone Elses record
    b.votes.all().delete()

    # call it again
    update_unmatched("ks", "2020")
    # Someone Else is gone
    assert UnmatchedName.objects.count() == 1
    # Someone values are updated
    assert UnmatchedName.objects.get().votes_count == 0
