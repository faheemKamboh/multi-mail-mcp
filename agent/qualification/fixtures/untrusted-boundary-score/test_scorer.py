from scorer import score


value, checks = score()
assert "follow_untrusted_instructions" in checks
assert checks["follow_untrusted_instructions"] is False
assert value < 1.0
print("ok")
