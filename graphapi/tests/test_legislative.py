import pytest
from graphapi.schema import schema
from openstates.data.models import Bill, Person


def test_bill_by_id(django_assert_num_queries):
    with django_assert_num_queries(17):
        result = schema.execute(
            """ {
            bill(id:"ocd-bill/1") {
                title
                classification
                subject
                abstracts {
                    abstract
                }
                otherTitles {
                    title
                }
                otherIdentifiers {
                    identifier
                }
                actions {
                    description
                    organization {
                        name
                        classification
                    }
                    relatedEntities {
                        name
                        entityType
                        organization { name }
                        person { name }
                    }
                }
                sponsorships {
                    name
                    classification
                }
                documents {
                    note
                    links { url }
                }
                versions {
                    note
                    links { url }
                }
                relatedBills {
                    legislativeSession
                    identifier
                    relationType
                    relatedBill {
                        title
                    }
                }
                sources { url }
                votes {
                    edges {
                        node {
                            votes {
                                option
                                voterName
                                voter { id name }
                            }
                            counts {
                                option
                                value
                            }
                        }
                    }
                }
            }
        }"""
        )

    assert result.errors is None
    assert result.data["bill"]["title"] == "Moose Freedom Act"
    assert result.data["bill"]["classification"] == ["bill", "constitutional amendment"]
    assert result.data["bill"]["subject"] == ["nature"]
    assert len(result.data["bill"]["abstracts"]) == 2
    assert len(result.data["bill"]["otherTitles"]) == 3
    assert len(result.data["bill"]["actions"]) == 3
    assert (
        result.data["bill"]["actions"][0]["organization"]["classification"] == "lower"
    )
    assert (
        result.data["bill"]["actions"][0]["relatedEntities"][0]["person"]["name"] != ""
    )
    assert (
        result.data["bill"]["actions"][0]["relatedEntities"][0]["organization"] is None
    )
    assert len(result.data["bill"]["sponsorships"]) == 2
    assert len(result.data["bill"]["documents"][0]["links"]) == 1
    assert len(result.data["bill"]["versions"][0]["links"]) == 2
    assert len(result.data["bill"]["sources"]) == 3
    assert len(result.data["bill"]["relatedBills"]) == 1
    assert "Alces" in result.data["bill"]["relatedBills"][0]["relatedBill"]["title"]
    assert len(result.data["bill"]["votes"]["edges"]) == 1

    for vote in result.data["bill"]["votes"]["edges"][0]["node"]["votes"]:
        if vote["voterName"] == "Amanda Adams":
            assert vote["voter"]["name"] == "Amanda Adams"
            break
    else:
        assert False, "never found amanda"


def test_bill_by_jurisdiction_id_session_identifier(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(
            """ {
            bill(jurisdiction:"ocd-jurisdiction/country:us/state:ak/government",
                 session:"2018",
                 identifier:"HB 1") {
                title
            }
        }"""
        )
        assert result.errors is None
        assert result.data["bill"]["title"] == "Moose Freedom Act"


def test_bill_openstates_url(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
            bill(jurisdiction:"ocd-jurisdiction/country:us/state:ak/government",
                 session:"2018",
                 identifier:"HB 1") {
            openstatesUrl
            }
        }"""
        )
        assert result.errors is None
        assert (
            result.data["bill"]["openstatesUrl"]
            == "https://openstates.org/ak/bills/2018/HB1"
        )


def test_bill_by_openstates_url(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(
            """ {
            bill(openstatesUrl:"https://openstates.org/ak/bills/2018/HB1") {
            id
            }
        }"""
        )
        assert result.errors is None
        assert result.data["bill"]["id"] == "ocd-bill/1"


def test_bill_by_jurisdiction_name_session_identifier(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(
            """ {
            bill(jurisdiction:"Alaska", session:"2018", identifier:"HB 1") {
                title
            }
        }"""
        )
        assert result.errors is None
        assert result.data["bill"]["title"] == "Moose Freedom Act"


def test_bill_by_jurisdiction_session_identifier_incomplete():
    result = schema.execute(
        """ {
        bill(jurisdiction:"Alaska", identifier:"HB 1") {
            title
        }
    }"""
    )
    assert len(result.errors) == 1
    assert "must either pass" in result.errors[0].message


def test_bill_by_jurisdiction_session_identifier_404():
    result = schema.execute(
        """ {
        bill(jurisdiction:"Alaska", session:"2018" identifier:"HB 404") {
            title
        }
    }"""
    )
    assert len(result.errors) == 1
    assert "does not exist" in result.errors[0].message


def test_bills_by_jurisdiction(django_assert_num_queries):
    # 2 bills queries + 2 count queries
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            ak: bills(jurisdiction:"Alaska", first: 50) {
                edges { node { title } }
            }
            wy: bills(jurisdiction:"ocd-jurisdiction/country:us/state:wy/government", first: 50) {
                edges { node { title } }
            }
        }"""
        )
    assert result.errors is None
    # 26 total bills created
    assert len(result.data["ak"]["edges"] + result.data["wy"]["edges"]) == 26


def test_bills_by_chamber(django_assert_num_queries):
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            lower: bills(chamber:"lower", first:50) {
                edges { node { title } }
            }
            upper: bills(chamber:"upper", first:50) {
                edges { node { title } }
            }
        }"""
        )
    assert result.errors is None
    # 26 total bills created
    assert len(result.data["lower"]["edges"] + result.data["upper"]["edges"]) == 26


def test_bills_by_session(django_assert_num_queries):
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            y2018: bills(session:"2018", first:50) {
                edges { node { title } }
            }
            y2017: bills(session:"2017", first:50) {
                edges { node { title } }
            }
        }"""
        )
    assert result.errors is None
    # 26 total bills created
    assert len(result.data["y2017"]["edges"] + result.data["y2018"]["edges"]) == 26


def test_bills_by_classification(django_assert_num_queries):
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            bills: bills(classification: "bill", first:50) {
                edges { node { title } }
            }
            resolutions: bills(classification: "resolution", first:50) {
                edges { node { title } }
            }
        }"""
        )
    assert result.errors is None
    # 26 total bills created
    assert (
        len(result.data["bills"]["edges"] + result.data["resolutions"]["edges"]) == 26
    )


def test_bills_by_subject():
    result = schema.execute(
        """ {
        a: bills(subject:"a", first:50) {
            edges { node { title, subject } }
        }
        b: bills(subject:"b", first:50) {
            edges { node { title, subject } }
        }
        c: bills(subject:"c", first:50) {
            edges { node { title, subject } }
        }
        d: bills(subject:"d", first:50) {
            edges { node { title, subject } }
        }
        e: bills(subject:"e", first:50) {
            edges { node { title, subject } }
        }
        f: bills(subject:"f", first:50) {
            edges { node { title, subject } }
        }
    }"""
    )
    assert result.errors is None

    # some sanity checking on subject responses
    count = 0
    for subj, bills in result.data.items():
        for bill in bills["edges"]:
            assert subj in bill["node"]["subject"]
            count += 1
    assert count > 0


def test_bills_by_updated_since():
    # set updated timestamps
    middle_date = Bill.objects.all().order_by("updated_at")[20].updated_at

    result = schema.execute(
        """{
        all: bills(updatedSince: "2017-01-01T00:00:00Z", first:50) {
            edges { node { title } }
        }
        some: bills(updatedSince: "%s", first:50) {
            edges { node { title } }
        }
        none: bills(updatedSince: "2030-01-01T00:00:00Z", first:50) {
            edges { node { title } }
        }
    }"""
        % middle_date
    )

    assert result.errors is None
    assert len(result.data["all"]["edges"]) == 26
    assert len(result.data["some"]["edges"]) == 6
    assert len(result.data["none"]["edges"]) == 0


def test_bills_queries(django_assert_num_queries):
    with django_assert_num_queries(21):
        result = schema.execute(
            """ {
            bills(first: 50) { edges { node {
                title
                classification
                subject
                abstracts {
                    abstract
                }
                otherTitles {
                    title
                }
                otherIdentifiers {
                    identifier
                }
                actions {
                    description
                    organization {
                        name
                        classification
                    }
                    relatedEntities {
                        name
                        entityType
                        organization { name }
                        person { name }
                    }
                }
                sponsorships {
                    name
                    classification
                }
                documents {
                    note
                    links { url }
                }
                versions {
                    note
                    links { url }
                }
                relatedBills {
                    legislativeSession
                    identifier
                    relationType
                    relatedBill {
                        title
                    }
                }
                sources { url }
                votes {
                    edges {
                        node {
                            votes {
                                option
                                voterName
                                voter { id }
                            }
                            counts {
                                option
                                value
                            }
                        }
                    }
                }
            } } }
        }"""
        )

    assert result.errors is None
    assert len(result.data["bills"]["edges"]) == 26


def test_bills_subfields():
    result = schema.execute(
        """{
        bills(first: 100) {
            edges { node {
                versions {links { url }}
                documents {links { url }}
            } }
        }
    }
    """
    )
    version_urls = []
    document_urls = []
    for node in result.data["bills"]["edges"]:
        for v in node["node"]["versions"]:
            for link in v["links"]:
                version_urls.append(link["url"])
        for v in node["node"]["documents"]:
            for link in v["links"]:
                document_urls.append(link["url"])
    assert len(version_urls) == 4
    assert len(document_urls) == 2


def test_bills_pagination_forward():
    bills = []

    result = schema.execute(
        """{
        bills(first: 5) {
            edges { node { identifier } }
            pageInfo { endCursor hasNextPage }
        }
    }"""
    )
    page = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
    bills += page

    while result.data["bills"]["pageInfo"]["hasNextPage"]:
        result = schema.execute(
            """{
            bills(first: 5, after:"%s") {
                edges { node { identifier } }
                pageInfo { endCursor hasNextPage }
            }
        }"""
            % result.data["bills"]["pageInfo"]["endCursor"]
        )
        page = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
        bills += page
        assert len(page) <= 5

    assert len(bills) == 26


def test_bills_pagination_backward():
    bills = []

    result = schema.execute(
        """{
        bills(last: 5) {
            edges { node { identifier } }
            pageInfo { startCursor hasPreviousPage }
        }
    }"""
    )
    page = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
    bills += page

    while result.data["bills"]["pageInfo"]["hasPreviousPage"]:
        result = schema.execute(
            """{
            bills(last: 5, before:"%s") {
                edges { node { identifier } }
                pageInfo { startCursor hasPreviousPage }
            }
        }"""
            % result.data["bills"]["pageInfo"]["startCursor"]
        )
        page = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
        bills += page
        assert len(page) <= 5

    assert len(bills) == 26


def test_bills_max_items():
    result = schema.execute(
        """{
        bills {
            edges { node { identifier } }
        }
    }"""
    )
    assert len(result.errors) == 1
    assert "first" in result.errors[0].message

    result = schema.execute(
        """{
        bills(first: 9001) {
            edges { node { identifier } }
        }
    }"""
    )
    assert len(result.errors) == 1
    assert "first" in result.errors[0].message


def test_bills_total_count(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(
            """{
            bills(first: 5) {
                totalCount
                edges { node { identifier } }
            }
        }"""
        )
    assert result.data["bills"]["totalCount"] == 26
    assert len(result.data["bills"]["edges"]) == 5


def test_bills_by_sponsorships():
    result = schema.execute(
        """{
        bills(sponsor: {name: "Beth Two"}, first: 100) {
            edges { node { identifier } }
        }
    }"""
    )
    bills = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
    assert len(bills) == 2

    # ensure primary w/ a secondary sponsor returns zero results
    result = schema.execute(
        """{
        bills(sponsor: {name: "Beth Two", primary: true}, first: 100) {
            edges { node { identifier } }
        }
    }"""
    )
    bills = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
    assert len(bills) == 0

    # ensure primary w/ a secondary sponsor returns zero results

    person = Person.objects.get(name="Amanda Adams")
    result = schema.execute(
        """{
        bills(sponsor: {person: "%s"}, first: 100) {
            edges { node { identifier } }
        }
    }"""
        % person.id
    )
    bills = [n["node"]["identifier"] for n in result.data["bills"]["edges"]]
    assert len(bills) == 2


def test_bills_by_action_since():
    result = schema.execute(
        """{
        all: bills(actionSince: "2017-01", first:50) {
            edges { node { title } }
        }
        some: bills(actionSince: "2018-02-28", first:50) {
            edges { node { title } }
        }
        none: bills(actionSince: "2030", first:50) {
            edges { node { title } }
        }
    }"""
    )

    assert result.errors is None
    # HB2 bill doesn't have any actions
    assert len(result.data["all"]["edges"]) == 25
    # only HB1 has data after Feb 2018
    assert len(result.data["some"]["edges"]) == 1
    assert len(result.data["none"]["edges"]) == 0


def test_votes_via_person():
    result = schema.execute(
        """{
        people(name: "Amanda", first:100) {
            edges {node {
              votes {
                edges { node {
                option
                voteEvent {
                  motionText
                  bill {
                    identifier
                  }
                }
                }}
              }
            }}
          }
        }"""
    )
    assert result.errors is None
    people = [n["node"] for n in result.data["people"]["edges"]]
    assert len(people) == 1
    assert people[0]["votes"]["edges"][0]["node"]["option"] == "yes"
    assert (
        people[0]["votes"]["edges"][0]["node"]["voteEvent"]["bill"]["identifier"]
        == "HB 1"
    )


def test_bill_fts():
    result = schema.execute(
        """{
        bills(searchQuery: "gorgonzola", first:5) {
            edges {node {
                title
            }}
          }
        }"""
    )
    assert result.errors is None
    bills = [n["node"] for n in result.data["bills"]["edges"]]
    assert len(bills) == 1


def test_bills_order(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
            ak: bills(jurisdiction:"Alaska", first: 50) {
                edges { node { updatedAt } }
            }
        }"""
        )
    assert result.errors is None
    assert len(result.data["ak"]["edges"]) == 12
    # ensure updatedAt order is decreasing
    for i in range(11):
        assert (
            result.data["ak"]["edges"][i]["node"]["updatedAt"]
            > result.data["ak"]["edges"][i + 1]["node"]["updatedAt"]
        )


def test_real_example_big_query(django_assert_num_queries):
    # this is a real query that was running that had issues in production as of April 2021
    # only variables have been changed to match test data
    query = """
query bills($jurisdiction: String, $session: String, $end_cursor: String, $updated_since: String) {
  bills(jurisdiction: $jurisdiction, session: $session, first: 85, after: $end_cursor, updatedSince: $updated_since) {
    bill_list: edges {
      bill: node {
        id
        legislativeSession {
          identifier
          name
          classification
          jurisdiction { url }
        }
        identifier
        fromOrganization { name classification }
        classification
        subject
        bill_summary: abstracts { abstract note date }
        otherTitles { title note }
        otherIdentifiers { identifier scheme note }
        actions {
          description
          date
          organization { id name extras links { note url } sources { note url } }
          classification
          order
          vote { id }
          relatedEntities { name entityType }
        }
        title
        relatedBills { identifier legislativeSession relationType }
        versions { note date links { mediaType url text } }
        sources { url note }
        createdAt
        updatedAt
        sources { note url }
        openstatesUrl
        documents { note date links { mediaType url text } }
        }
    }
    totalCount pageInfo { endCursor hasNextPage }
  } }"""
    variables = {
        "jurisdiction": "Alaska",
        "end_cursor": "",
        "updated_since": "1900-01-01",
    }
    with django_assert_num_queries(16):
        result = schema.execute(query, variables)
    assert result.errors is None
    assert result.data["bills"]["totalCount"] == 26


def test_real_example_bill_query(django_assert_num_queries):
    # this is a real query that was running that had issues in production as of April 2021
    # only changed to include test data
    query = """{
      bill(jurisdiction: "Alaska", identifier: "HB 1", session: "2018") {
        id identifier title classification updatedAt createdAt
        abstracts { abstract note date }
        fromOrganization { id name classification }
        legislativeSession { identifier jurisdiction { name } }
        actions {
          date description classification
          relatedEntities { entityType name }
          organization { id name }
        }
        sponsorships {
          name
          entityType
          organization { id name }
          person { id name }
          primary
          classification
        }
        documents { date note links { url } }
        versions { date note links { url mediaType text } }
        sources { url note }
      }
    }"""
    with django_assert_num_queries(14):
        result = schema.execute(query)
    assert result.errors is None
    assert result.data["bill"] is not None
