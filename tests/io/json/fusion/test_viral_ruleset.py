import msgspec

from pysdmx.io.json.fusion.messages.vtl import FusionRuleset


def test_viral_propagation():
    payload = (
        b'{"id": "VP", "names": [{"locale": "en", "value": "Viral"}], '
        b'"rulesetDefinition": "define viral propagation VP (variable '
        b'OBS_STATUS) is else \\"A\\" end viral propagation", '
        b'"rulesetType": "viral", "rulesetScope": "variable"}'
    )

    ruleset = msgspec.json.decode(payload, type=FusionRuleset).to_model()

    assert ruleset.id == "VP"
    assert ruleset.ruleset_type == "viral"
