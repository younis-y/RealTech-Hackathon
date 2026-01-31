# 06 Error Handling & Self-Annealing
## System Resilience and Automated Recovery

### Purpose
Define error handling strategies and the self-annealing loop that makes the system stronger after each failure.

---

## Self-Annealing Loop

When ANY tool fails or produces unexpected output:

```
1. ANALYZE
   ├─ Read full stack trace
   ├─ Identify root cause (API? Data? Logic?)
   └─ Determine if error is transient or systematic

2. PATCH
   ├─ Fix the Python script in tools/
   ├─ Add error handling if missing
   └─ Implement retry logic if needed

3. TEST
   ├─ Run tool with original failing input
   ├─ Verify fix resolves the issue
   └─ Test edge cases related to the error

4. UPDATE SOP
   ├─ Document learning in relevant architecture/*.md
   ├─ Add error pattern to this file
   └─ Update rate limits/constraints if discovered

5. LOG TO GEMINI.MD
   ├─ Add entry to Self-Annealing Log table
   ├─ Include: Date, Error, Root Cause, Fix, SOP Updated
   └─ System is now stronger ✅
```

**Never skip steps 4 and 5.** The system learns only when errors are documented.

---

## Error Categories

### 1. API Errors

#### Authentication Failures (401, 403)
**Symptoms**: "Unauthorized", "Forbidden"
**Root Causes**:
- Invalid API key in .env
- Expired token
- Wrong authentication method

**Fix Pattern**:
```python
if response.status_code in [401, 403]:
    raise ValueError(
        f"Authentication failed for {api_name}. "
        f"Check {env_var_name} in .env file."
    )
```

**User Action Required**: Update .env with valid key

#### Rate Limiting (429, 503)
**Symptoms**: "Too Many Requests", "Service Unavailable"
**Root Causes**:
- Exceeded API rate limit
- Server overload

**Fix Pattern**:
```python
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    print(f"[WARNING] Rate limited. Retrying after {retry_after}s")
    time.sleep(retry_after)
    # Retry request
```

**Prevention**:
- Add delays between requests
- Implement exponential backoff
- Use caching aggressively

#### Resource Not Found (404)
**Symptoms**: "Not Found"
**Root Causes**:
- Invalid area code/postcode
- Resource doesn't exist in API

**Fix Pattern**:
```python
if response.status_code == 404:
    print(f"[WARNING] {resource} not found in {api_name}")
    return None  # Return null, continue with other areas
```

**Prevention**: Validate input format before API call

#### Server Errors (500, 502, 503, 504)
**Symptoms**: "Internal Server Error", "Bad Gateway"
**Root Causes**:
- API service down
- Temporary outage

**Fix Pattern**:
```python
if response.status_code >= 500:
    if attempt < max_retries:
        backoff = 2 ** attempt
        print(f"[ERROR] Server error. Retrying in {backoff}s...")
        time.sleep(backoff)
        # Retry
    else:
        raise Exception(f"API unavailable after {max_retries} attempts")
```

### 2. Data Errors

#### Missing Required Fields
**Symptoms**: KeyError, None values in critical fields
**Root Causes**:
- API response structure changed
- Data not available for this area

**Fix Pattern**:
```python
# Don't do this:
score = data["affordability_score"]  # Can raise KeyError

# Do this:
score = data.get("affordability_score", 50)  # Default to neutral
if score is None:
    score = 50
    print(f"[WARNING] Missing affordability_score for {area_code}")
```

**Update SOP**: Document which fields are optional

#### Invalid Data Types
**Symptoms**: TypeError, ValueError
**Root Causes**:
- String where number expected
- Null where value expected

**Fix Pattern**:
```python
try:
    price = float(data.get("avg_price", 0))
except (ValueError, TypeError):
    print(f"[WARNING] Invalid price data: {data.get('avg_price')}")
    price = 0  # or None
```

#### Out-of-Range Values
**Symptoms**: Scores > 100, negative prices
**Root Causes**:
- API data error
- Calculation bug

**Fix Pattern**:
```python
def normalize_score(value, min_val=0, max_val=100):
    """Clamp value to range [min_val, max_val]"""
    if value is None:
        return 50  # Neutral default
    return max(min_val, min(max_val, value))
```

### 3. Network Errors

#### Timeout
**Symptoms**: requests.exceptions.Timeout
**Root Causes**:
- Slow API response
- Network issues

**Fix Pattern**:
```python
try:
    response = requests.get(url, timeout=30)
except requests.exceptions.Timeout:
    print(f"[ERROR] Request timeout for {url}")
    # Retry with longer timeout
    response = requests.get(url, timeout=60)
```

#### Connection Error
**Symptoms**: requests.exceptions.ConnectionError
**Root Causes**:
- No internet connection
- API endpoint down

**Fix Pattern**:
```python
try:
    response = requests.get(url)
except requests.exceptions.ConnectionError:
    print(f"[ERROR] Cannot connect to {url}")
    # Try fallback API or return cached data
    return load_from_cache(cache_key)
```

### 4. Logic Errors

#### Division by Zero
**Symptoms**: ZeroDivisionError
**Fix Pattern**:
```python
# Don't do this:
ratio = numerator / denominator

# Do this:
ratio = numerator / denominator if denominator != 0 else 0
```

#### Empty List Operations
**Symptoms**: IndexError, ValueError (max() on empty list)
**Fix Pattern**:
```python
# Don't do this:
top_score = max(scores)

# Do this:
top_score = max(scores) if scores else 0
```

---

## Graceful Degradation Strategy

**Principle**: One component failure should not crash entire pipeline.

### Example: Scoring Engine

```python
def score_area(area_code, persona):
    """Score an area, degrading gracefully if data is missing."""
    scores = {}

    # ScanSan (critical)
    try:
        scansan_data = fetch_scansan(area_code)
        if scansan_data:
            scores["affordability"] = scansan_data.get("affordability_score", 50)
            scores["investment"] = scansan_data.get("investment_quality", 50)
        else:
            print(f"[ERROR] No ScanSan data for {area_code}. Skipping area.")
            return None  # ScanSan is critical; can't score without it
    except Exception as e:
        print(f"[ERROR] ScanSan API failed: {e}")
        return None

    # Commute (important but not critical)
    try:
        commute_data = fetch_tfl_commute(area_code, destination)
        scores["commute"] = calculate_commute_score(commute_data)
    except Exception as e:
        print(f"[WARNING] TfL failed for {area_code}: {e}. Using default commute score.")
        scores["commute"] = 50  # Neutral score if can't fetch

    # Crime (important but not critical)
    try:
        crime_data = fetch_crime_data(area_code)
        scores["safety"] = crime_data.get("safety_score", 50)
    except Exception as e:
        print(f"[WARNING] Crime data failed for {area_code}: {e}")
        scores["safety"] = 50

    # Amenities (nice to have)
    try:
        amenities = fetch_amenities(area_code, persona)
        scores["amenities"] = amenities.get("density_score", 50)
    except Exception as e:
        print(f"[WARNING] Amenities failed for {area_code}: {e}")
        scores["amenities"] = 50

    # Calculate composite score (even with some missing data)
    composite = calculate_weighted_score(scores, persona)
    return {"area_code": area_code, "scores": scores, "composite": composite}
```

**Key Points**:
- Critical data (ScanSan): Return None if fails
- Important data (TfL, crime): Use default neutral score
- Nice-to-have (amenities): Use default neutral score
- Log all warnings so we can investigate later

---

## Logging Standards

### Console Logging Levels

```python
print("[INFO] Starting data fetch for 10 areas...")      # Normal operation
print("[WARNING] Rate limited. Retrying in 60s...")      # Non-critical issue
print("[ERROR] API authentication failed. Check .env")   # Critical issue
```

### File Logging

**For Errors**: Update `gemini.md` Self-Annealing Log
**For Costs**: Update `.tmp/api_costs_log.json`
**For Cache**: Automatic via `tools/cache_manager.py`

### Never Log Secrets

```python
# ❌ NEVER do this:
print(f"API key: {SCANSAN_API_KEY}")

# ✅ Do this:
print(f"API key: {SCANSAN_API_KEY[:8]}...")  # First 8 chars only
```

---

## Testing Error Scenarios

### Unit Tests for Error Handling

```python
# test_fetch_scansan.py
def test_invalid_api_key():
    """Test that tool raises clear error with invalid key."""
    with pytest.raises(ValueError, match="Authentication failed"):
        fetch_scansan("SW1A", api_key="invalid_key_123")

def test_missing_area():
    """Test that tool returns None for non-existent area."""
    result = fetch_scansan("INVALID999")
    assert result is None

def test_rate_limit_retry():
    """Test that tool retries on rate limit."""
    # Mock 429 response, then 200 response
    result = fetch_scansan("SW1A")
    assert result is not None  # Should succeed after retry
```

### Integration Tests

Create `tools/test_error_recovery.py`:
- Test full pipeline with one API failing
- Verify system continues with degraded data
- Verify output includes warnings about missing data

---

## Recovery Procedures

### When All APIs Fail

**Scenario**: Internet outage, all external APIs unreachable

**Recovery**:
1. Load cached data from `.tmp/`
2. Return results with disclaimer: "Using cached data from [date]"
3. Reduce cache validity to 1 hour (fresher data needed)
4. Retry APIs every 5 minutes in background

### When Cache is Empty

**Scenario**: First run, no cache available, APIs failing

**Recovery**:
1. Return error to user: "Unable to fetch data. Please try again in a few minutes."
2. Don't proceed with empty/default scores (misleading)
3. Log incident to `gemini.md`
4. Alert developer (if in production)

### When Tool Logic is Broken

**Scenario**: Bug in `score_areas.py` causing crashes

**Self-Annealing Steps**:
1. AI analyzes stack trace
2. AI identifies bug (e.g., division by zero, wrong data type)
3. AI fixes `score_areas.py`
4. AI runs test with same input to verify fix
5. AI updates `architecture/02_scoring_engine.md` with edge case
6. AI logs fix to `gemini.md`
7. System now handles this case correctly ✅

---

## Monitoring & Alerts

### What to Monitor

- **API success rate**: Log every API call (success/fail)
- **API costs**: Track daily spend per service
- **Cache hit rate**: How often we avoid API calls
- **Error frequency**: Count errors by category
- **User-facing failures**: Any request that returned error to user

### Alert Thresholds

- API success rate < 95% → Investigate
- Daily API cost > £10 → Review caching strategy
- Cache hit rate < 50% → Increase cache duration
- Error frequency > 10/hour → Check API status pages

### Weekly Review

Every week, review:
1. `gemini.md` Self-Annealing Log
2. `.tmp/api_costs_log.json`
3. Architecture SOPs: Any needed updates?
4. Tools: Any needed refactoring?

---

## Documentation Template for New Errors

When encountering a NEW error pattern:

```markdown
### [Error Name]
**Discovered**: [Date]
**Symptoms**: [What user/developer sees]
**Root Cause**: [Why it happens]
**Fix Pattern**:
```python
[Code showing how to handle this error]
```
**Prevention**: [How to avoid in future]
**SOP Updated**: [Which architecture/*.md was updated]
**Test Added**: [What test now covers this case]
```

Add to this file under appropriate error category.

---

## Golden Rules

1. **Never crash silently**: Log every error
2. **Never guess**: If root cause unclear, investigate before fixing
3. **Always test**: Verify fix works before marking done
4. **Always document**: Update SOP and gemini.md
5. **Fail gracefully**: Return partial results > no results
6. **Cache is king**: Avoid redundant API calls that might fail

**Remember**: Every error is an opportunity to make the system stronger. The self-annealing loop ensures errors don't repeat.
