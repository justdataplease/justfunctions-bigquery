# Documentation for BigQuery Open Source library of UDFs Functions and Procedures | by JustDataPlease

## Contents
1. [clean_url(url)](#clean_url)
2. [split_url(url, part)](#split_url)
3. [fuzzy_nysiis(string)](#fuzzy_nysiis)
4. [surrogate_key(string)](#surrogate_key)
5. [word_distance(string_1, string_2)](#word_distance)
6. [parse_useragent(useragent)](#parse_useragent)
7. [surrogate_key_str(string)](#surrogate_key_str)
8. [extract_url_domain(url)](#extract_url_domain)
9. [extract_url_prefix(url)](#extract_url_prefix)
10. [extract_url_suffix(url)](#extract_url_suffix)
11. [fuzzy_distance_dam(string_1, string_2)](#fuzzy_distance_dam)
12. [fuzzy_distance_leven(string_1, string_2)](#fuzzy_distance_leven)
13. [extract_url_parameter(url, parameter)](#extract_url_parameter)
14. [detect_department_email(email)](#detect_department_email)
15. [extract_url_domain_base(url)](#extract_url_domain_base)
16. [detect_free_email_domain(email_domain)](#detect_free_email_domain)
17. [remove_email_plus_address(email)](#remove_email_plus_address)
18. [detect_useragent_device_type(useragent)](#detect_useragent_device_type)
19. [extract_url_path(url, clean_url_tail)](#extract_url_path)
20. [extract_url_tail(url)](#extract_url_tail)
21. [extract_url_language(url)](#extract_url_language)
22. [extract_all_url_parameters(url)](#extract_all_url_parameters)
23. [clean_email(email)](#clean_email)
24. [detect_free_email(email)](#detect_free_email)
25. [validate_email(email)](#validate_email)
26. [decode_url(url)](#decode_url)
27. [dedup_chars(string)](#dedup_chars)
28. [word_tokens(string, symbol)](#word_tokens)
29. [replace_urls(string, replacement)](#replace_urls)
30. [stemmer_greek(string)](#stemmer_greek)
31. [normalize_text(string)](#normalize_text)
32. [remove_accents(string)](#remove_accents)
33. [stemmer_porter(string)](#stemmer_porter)
34. [replace_html_tags(string, replacement)](#replace_html_tags)
35. [stemmer_lancaster(string)](#stemmer_lancaster)
36. [remove_en_stopwords(string)](#remove_en_stopwords)
37. [remove_extra_spaces(string)](#remove_extra_spaces)
38. [extract_email_domain(url)](#extract_email_domain)
39. [clean_special_symbols(string)](#clean_special_symbols)
40. [transliterate_anyascii(string)](#transliterate_anyascii)
41. [replace_en_contractions(string, replacement)](#replace_en_contractions)
42. [remove_extra_whitespaces(string)](#remove_extra_whitespaces)
43. [extract_email_domain_base(url)](#extract_email_domain_base)
44. [clean_special_symbols_custom(string)](#clean_special_symbols_custom)
45. [dedup_table(table_name, timestamp_column, unique_column, output_table_suffix)](#dedup_table)
46. [generate_justsql_schema(project_id, dataset_id, tables)](#generate_justsql_schema)
47. [percentile(arr, percentile)](#percentile)
48. [seconds_to_date(seconds)](#seconds_to_date)

---
## <a id='clean_url'></a>1. clean_url(url)

- **Type**: SQL
- **Tags**: text, new, url, featured
- **Region**: us,eu
- **Description**: Removes http/ftp/https:// and url tail and last url slash from a <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.clean_url`(`url` STRING) 
  RETURNS STRING AS (REGEXP_REPLACE(SPLIT(url,'?')[SAFE_OFFSET(0)],r'(https?|ftp):\/\/|\/$', ''))
  OPTIONS ( description = '''Removes http/ftp/https:// and url tail and last url slash from a <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.clean_url`("https://hey.com/me/?231#213")
```

**Example Output**:

```
hey.com/me
```
---
## <a id='split_url'></a>2. split_url(url, part)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Splits a <url> into parts, using '/' symbol.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.split_url`(`url` STRING, `part` INT) 
  RETURNS STRING AS ((WITH split_parts as (
SELECT SPLIT("/" || TRIM(url,"/"), "/") split_str
)
SELECT split_str[safe_ordinal(part+1)]
from split_parts)
)
  OPTIONS ( description = '''Splits a <url> into parts, using '/' symbol.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.split_url`("hey.com/me/?231#213","2")
```

**Example Output**:

```
me
```
---
## <a id='fuzzy_nysiis'></a>3. fuzzy_nysiis(string)

- **Type**: SQL
- **Tags**: text, similarity
- **Region**: us,eu
- **Description**: Calculates NYSIIS code for <string>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.fuzzy_nysiis`(`string` STRING) 
  RETURNS STRING AS (((
select
  string_agg(c, "" order by off asc)
from (select
        c,
        off,
        coalesce(lag(c) over (order by off) = c, false) as same_as_prev_char
      from unnest(split((select
              regexp_replace(regexp_replace(regexp_replace(string_agg(new_c, "" order by off), r"s+$", ""), "ay$", "y"), "a+$", "") as step_7
            from (select
                    c,
                    if(off = 0, c, 
                    case 
                      when off != 0 and c = 'e' and next_c = 'v' then 'a'
                      when off != 1 and c = 'v' and prev_c = 'e' then 'f'

                      when c in ('a', 'e', 'i', 'o', 'u') then 'a'

                      when c = 'q' then 'g'
                      when c = 'z' then 's'
                      when c = 'm' then 'n'

                      when c = 'k' and next_c = 'n' then 'n'
                      when off != 1 and prev_c = 'k' and c = 'n' then null
                      when c = 'k' then 'c'

                      when c = 's' and next_c = 'c' and next2_c = 'h' then 's'
                      when off != 1 and prev_c = 's' and c = 'c' and next_c = 'h' then 's'
                      when off != 2 and prev2_c = 's' and prev_c = 'c' and c = 'h' then 's'

                      when c = 'p' and next_c = 'h' then 'f'
                      when off != 1 and prev_c = 'p' and c = 'h' then 'f'

                      when off != 1 and (c = 'h' and (prev_c not in ('a', 'e', 'i', 'o', 'u') or next_c not in ('a', 'e', 'i', 'o', 'u'))) then prev_c
                      when off != 1 and c = 'w' and prev_c in ('a', 'e', 'i', 'o', 'u') then prev_c
                      else c
                    end) as new_c,
                    off
                  from (select
                          c,
                          off,
                          lag(c) over (order by off) as prev_c,
                          lag(c, 2) over (order by off) as prev2_c,
                          lead(c) over (order by off) as next_c,
                          lead(c, 2) over (order by off) as next2_c
                        from unnest(split(regexp_replace(regexp_replace(regexp_replace(
                                          regexp_replace(regexp_replace(regexp_replace(
                                          regexp_replace(lower(string), "^mac", "mcc"),
                                                          "^kn", "nn"),
                                                          "^k", "c"),
                                                          "^p(h|f)", "ff"),
                                                          "^sch", "sss"),
                                                          "(e|i)e$", "y"),
                                                          "(dt|rt|rd|nt|nd)$", "d")
                                      , "")) as c with offset off -- starts at 0
                        )
                  )
            where new_c is not null
            ), "")) as c with offset off
      )
where ((not same_as_prev_char) or (same_as_prev_char and off = 1))
)))
  OPTIONS ( description = '''Calculates NYSIIS code for <string>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.fuzzy_nysiis`("python")
```

**Example Output**:

```
pytan
```
---
## <a id='surrogate_key'></a>4. surrogate_key(string)

- **Type**: SQL
- **Tags**: text, surrogate key
- **Region**: us,eu
- **Description**: Creates a hashed value of multiple field <string>. Use CONCAT to create <string> to include multiple fields.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.surrogate_key`(`string` STRING) 
  RETURNS INT64 AS (CAST(FARM_FINGERPRINT(string) AS INT64))
  OPTIONS ( description = '''Creates a hashed value of multiple field <string>. Use CONCAT to create <string> to include multiple fields.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.surrogate_key`("python")
```

**Example Output**:

```
2065202487608477923
```
---
## <a id='word_distance'></a>5. word_distance(string_1, string_2)

- **Type**: JS
- **Tags**: text, similarity
- **Region**: us,eu
- **Description**: Calculates Levenshtein distance between <string_1> and <string_2>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.word_distance`(`string_1` STRING, `string_2` STRING) RETURNS INT64
	LANGUAGE js AS r'''return fuzzball.distance(string_1,string_2);''' OPTIONS ( description = '''Calculates Levenshtein distance between <string_1> and <string_2>.'''  , library = [  "gs://justfunctions/bigquery-functions/fuzzball.umd.min.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.word_distance`("python","pithon")
```

**Example Output**:

```
1
```
---
## <a id='parse_useragent'></a>6. parse_useragent(useragent)

- **Type**: JS
- **Tags**: text, useragent, new
- **Region**: us,eu
- **Description**: Parses UserAgent details from <useragent>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.parse_useragent`(`useragent` STRING) RETURNS STRUCT<
browser STRUCT<name STRING, version STRING, major STRING>,
engine  STRUCT<name STRING, version STRING>,
os      STRUCT<name STRING, version STRING>,
device  STRUCT<vendor STRING, model STRING, type STRING>,
arch    STRING
>

	LANGUAGE js AS r'''let a = UAParser(useragent);
a.arch = a.cpu.architecture;
return a;
''' OPTIONS ( description = '''Parses UserAgent details from <useragent>.'''  , library = [  "gs://justfunctions/bigquery-functions/ua-parser.min.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.parse_useragent`("Mozilla/5.0 (iPad; CPU OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1")
```

**Example Output**:

```
name : Mobile Safari |
browser.version : 12.1.2 |
browser.major : 12 |
engine.name : WebKit |
engine.version : 605.1.15 |
os.name : iOS |
os.version : 12.5.7 |
device.vendor : Apple |
device.model : iPad |
device.type : tablet |
arch : null

```
---
## <a id='surrogate_key_str'></a>7. surrogate_key_str(string)

- **Type**: SQL
- **Tags**: text, surrogate key
- **Region**: us,eu
- **Description**: Creates a hashed value of multiple field <string>. Use CONCAT to create <string> to include multiple fields.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.surrogate_key_str`(`string` STRING) 
  RETURNS STRING AS (CAST(FARM_FINGERPRINT(string) AS STRING))
  OPTIONS ( description = '''Creates a hashed value of multiple field <string>. Use CONCAT to create <string> to include multiple fields.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.surrogate_key_str`("python")
```

**Example Output**:

```
2065202487608477923
```
---
## <a id='extract_url_domain'></a>8. extract_url_domain(url)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Extract the domain of a <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_domain`(`url` STRING) 
  RETURNS STRING AS (NET.REG_DOMAIN(url))
  OPTIONS ( description = '''Extract the domain of a <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_domain`("https://hey.com/me/?231#213")
```

**Example Output**:

```
hey.com
```
---
## <a id='extract_url_prefix'></a>9. extract_url_prefix(url)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Extracts url prefix from <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_prefix`(`url` STRING) 
  RETURNS STRING AS (SPLIT(url,".")[OFFSET(0)])
  OPTIONS ( description = '''Extracts url prefix from <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_prefix`("https://en.hey.com/me/?231#213")
```

**Example Output**:

```
en
```
---
## <a id='extract_url_suffix'></a>10. extract_url_suffix(url)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Extracts url suffix from <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_suffix`(`url` STRING) 
  RETURNS STRING AS (NET.PUBLIC_SUFFIX(url))
  OPTIONS ( description = '''Extracts url suffix from <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_suffix`("https://en.hey.com/me/?231#213")
```

**Example Output**:

```
com
```
---
## <a id='fuzzy_distance_dam'></a>11. fuzzy_distance_dam(string_1, string_2)

- **Type**: JS
- **Tags**: text, similarity
- **Region**: us,eu
- **Description**: Calculates Damerau-Levenshtein distance between <string_1> and <string_2>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.fuzzy_distance_dam`(`string_1` STRING, `string_2` STRING) RETURNS INT64
	LANGUAGE js AS r'''const initMatrix = (string_1, string_2) => {
  if (undefined == string_1 || undefined == string_2) {
    return null;
  }
  let d = [];
  for (let i = 0; i <= string_1.length; i++) {
    d[i] = [];
    d[i][0] = i;
  }
  for (let j = 0; j <= string_2.length; j++) {
    d[0][j] = j;
  }
  return d;
};
const damerau = (i, j, string_1, string_2, d, cost) => {
  if (i > 1 && j > 1 && string_1[i - 1] === string_2[j - 2] && string_1[i - 2] === string_2[j - 1]) {
    d[i][j] = Math.min.apply(null, [d[i][j], d[i - 2][j - 2] + cost]);
  }
};
if (
  undefined == string_1 ||
  undefined == string_2 ||
  "string" !== typeof string_1 ||
  "string" !== typeof string_2
) {
  return -1;
}
let d = initMatrix(string_1, string_2);
if (null === d) {
  return -1;
}
for (var i = 1; i <= string_1.length; i++) {
  let cost;
  for (let j = 1; j <= string_2.length; j++) {
    if (string_1.charAt(i - 1) === string_2.charAt(j - 1)) {
      cost = 0;
    } else {
      cost = 1;
    }
    d[i][j] = Math.min.apply(null, [
      d[i - 1][j] + 1,
      d[i][j - 1] + 1,
      d[i - 1][j - 1] + cost
    ]);
    damerau(i, j, string_1, string_2, d, cost);
  }
}
return d[string_1.length][string_2.length];''' OPTIONS ( description = '''Calculates Damerau-Levenshtein distance between <string_1> and <string_2>.'''  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.fuzzy_distance_dam`("pyhtno","python")
```

**Example Output**:

```
2
```
---
## <a id='fuzzy_distance_leven'></a>12. fuzzy_distance_leven(string_1, string_2)

- **Type**: JS
- **Tags**: text, similarity
- **Region**: us,eu
- **Description**: Calculates Levenshtein distance between <string_1> and <string_2>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.fuzzy_distance_leven`(`string_1` STRING, `string_2` STRING) RETURNS INT64
	LANGUAGE js AS r'''return fuzzball.distance(string_1,string_2);''' OPTIONS ( description = '''Calculates Levenshtein distance between <string_1> and <string_2>.'''  , library = [  "gs://justfunctions/bigquery-functions/fuzzball.umd.min.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.fuzzy_distance_leven`("pyhtno","python")
```

**Example Output**:

```
3
```
---
## <a id='extract_url_parameter'></a>13. extract_url_parameter(url, parameter)

- **Type**: SQL
- **Tags**: text, URL, new
- **Region**: us,eu
- **Description**: Extracts parameter value from <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_parameter`(`url` STRING, `parameter` STRING) 
  RETURNS STRING AS (REGEXP_EXTRACT(url, "[?&]" || parameter || "=([^&]+)"))
  OPTIONS ( description = '''Extracts parameter value from <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_parameter`("www.google.com?medium=cpc&source=google&keyword=hey&source=facebook","source")
```

**Example Output**:

```
facebook
```
---
## <a id='detect_department_email'></a>14. detect_department_email(email)

- **Type**: SQL
- **Tags**: text, email
- **Region**: us,eu
- **Description**: Detects if an <email> belongs to a business department (sales, hr, support etc).

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.detect_department_email`(`email` STRING) 
  RETURNS INT AS (((
     WITH A AS (SELECT SPLIT(email,"@")[offset(0)] email_part)

     SELECT 
     CASE 
        WHEN email_part IN (
           'info', 'test', 'hello', 'hey', 'help', 
           'press', 'support', 'sales', 'dev', 'developers', 'marketing', 
           'admin', 'hq', 'finance', 'operations', 'home', 'headquarters', 
           'jobs', 'main', 'here', 'one', 'hr', 'tech', 'billing', 
           'accounts', 'partnerships', 'team', 'contact',
           'feedback', 'legal', 'solutions', 'services', 'training', 
           'products', 'careers', 'service', 'management', 'events', 
           'subscriptions', 'media', 'research', 'security', 'investor', 
           'relations', 'customerservice',  'bookings', 'reservations', 
           'licensing', 'advertising', 'affiliates', 
           'design', 'editor', 'collaborations', 'solutions', 'analytics',
           'client', 'membership', 'strategy', 'businessdev', 'feedback', 
           'office', 'customer', 'cs', 'outreach') 
        OR REGEXP_CONTAINS(email_part,'support')
        THEN 1 ELSE 0 END is_department_email 
        FROM A 
)))
  OPTIONS ( description = '''Detects if an <email> belongs to a business department (sales, hr, support etc).''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.detect_department_email`("sales@dev.io")
```

**Example Output**:

```
1
```
---
## <a id='extract_url_domain_base'></a>15. extract_url_domain_base(url)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Extract the domain base of a <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_domain_base`(`url` STRING) 
  RETURNS STRING AS (REPLACE (NET.REG_DOMAIN(url), CONCAT('.',NET.PUBLIC_SUFFIX(url)),""))
  OPTIONS ( description = '''Extract the domain base of a <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_domain_base`("https://hey.com/me/?231#213")
```

**Example Output**:

```
hey
```
---
## <a id='detect_free_email_domain'></a>16. detect_free_email_domain(email_domain)

- **Type**: SQL
- **Tags**: text, email, new
- **Region**: us,eu
- **Description**: Detects if <email_domain> belongs to a free email service (gmail, yahoo, outlook, etc).

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.detect_free_email_domain`(`email_domain` STRING) 
  RETURNS INT AS ((SELECT CASE WHEN CHAR_LENGTH(email_domain)<=1 OR LOWER(email_domain) IN ('10minutemail', '126', '21cn', '33mail', 'alice', 'aliyun', 'aol', 'arnet', 'att', 'bell', 'bellsouth', 'binkmail', 'bluewin', 'blueyonder', 'bol', 'bt', 'btinternet', 'burnermail', 'charter', 'club', 'cock', 'comcast', 'cox', 'daum', 'deadaddress', 'disroot', 'dropmail', 'e4ward', 'earthlink', 'email', 'eu', 'fakeinbox', 'fakemailgenerator', 'fastmail', 'fibertel', 'foxmail', 'free', 'freenet', 'freeserve', 'games', 'getnada', 'gishpuppy', 'globo', 'globomail', 'gmail', 'gmx', 'googlemail', 'guerrillamail', 'hanmail', 'hotmail', 'hush', 'hushmail', 'icloud', 'ig', 'iname', 'inbox', 'inboxalias', 'incognitomail', 'itelefonica', 'jetable', 'juno', 'keemail', 'laposte', 'lavabit', 'libero', 'list', 'live', 'love', 'mac', 'mail', 'mail2world', 'mailblocks', 'mailcatch', 'maildrop', 'mailexpire', 'mailfence', 'mailinator', 'mailmoat', 'mailnesia', 'mailnull', 'mailoo', 'me', 'mintemail', 'moakt', 'mohmal', 'msn', 'myspamless', 'mytrashmail', 'nate', 'naver', 'neuf', 'neverbox', 'nomail', 'notsharingmy', 'ntlworld', 'nym', 'o2', 'oi', 'onet', 'online', 'orange', 'outlook', 'pobox', 'pookmail', 'poste', 'posteo', 'prodigy', 'proton', 'qq', 'r7', 'rambler', 'rediffmail', 'rocketmail', 'rogers', 'runbox', 'safe-mail', 'sbcglobal', 'seznam', 'sfr', 'shaw', 'shieldemail', 'sina', 'sky', 'skynet', 'sohu', 'spam', 'spambog', 'spambox', 'spamcowboy', 'spamevader', 'spamex', 'spamgourmet', 'spamhole', 'spaml', 'spamoff', 'spamspot', 'spamthis', 'speedy', 'startmail', 'sympatico', 't-online', 'talktalk', 'techemail', 'telenet', 'teletu', 'temp', 'tempinbox', 'tempmail', 'temporaryemail', 'terra', 'thisisnotmyrealemail', 'throwawaymail', 'tin', 'tiscali', 'trashmail', 'tuta', 'tutamail', 'tutanota', 'tvcablenet', 'uol', 'verizon', 'vfemail', 'virgilio', 'virgin', 'voo', 'walla', 'wanadoo', 'web', 'wow', 'ya', 'yahoo', 'yandex', 'yeah', 'ygm', 'ymail', 'yopmail', 'zipmail', 'zoho') OR REGEXP_CONTAINS(email_domain,r'[0-9]') THEN 1 ELSE 0 END ))
  OPTIONS ( description = '''Detects if <email_domain> belongs to a free email service (gmail, yahoo, outlook, etc).''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.detect_free_email_domain`("gmail")
```

**Example Output**:

```
1
```
---
## <a id='remove_email_plus_address'></a>17. remove_email_plus_address(email)

- **Type**: SQL
- **Tags**: text, email
- **Region**: us,eu
- **Description**: Removes any sub-address (also known as plus addressing) from the <email>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.remove_email_plus_address`(`email` STRING) 
  RETURNS STRING AS (REGEXP_REPLACE(email,r'(\+\w+)(@)', r'\2'))
  OPTIONS ( description = '''Removes any sub-address (also known as plus addressing) from the <email>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.remove_email_plus_address`("hey+other@gmail.com")
```

**Example Output**:

```
hey@gmail.com
```
---
## <a id='detect_useragent_device_type'></a>18. detect_useragent_device_type(useragent)

- **Type**: SQL
- **Tags**: text, useragent, new
- **Region**: us,eu
- **Description**: Detects UserAgent device type from <useragent>. It can be table,mobile,pc,tv or other.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.detect_useragent_device_type`(`useragent` STRING) 
  RETURNS STRING AS (CASE 
  WHEN REGEXP_CONTAINS(useragent, r'(?i)(iPad|Tablet|Kindle|Tab|GT-P)') THEN 'tablet'
  WHEN REGEXP_CONTAINS(useragent, r'(?i)(Android)') AND NOT REGEXP_CONTAINS(useragent, r'(?i)(Mobile)') THEN 'tablet' 
  WHEN REGEXP_CONTAINS(useragent, r'(?i)(Mobile|iPhone|Android|Windows Phone)') THEN 'mobile'
  WHEN REGEXP_CONTAINS(useragent, r'(?i)(SmartTV|AppleTV|GoogleTV|HbbTV|netcast|NETTV|OpenTV|Tizen|Web0S|SonyDTV)') THEN 'tv'
  WHEN REGEXP_CONTAINS(useragent, r'(?i)(Windows NT|Macintosh|Linux|X11)') THEN 'pc'
  ELSE 'other'
END
)
  OPTIONS ( description = '''Detects UserAgent device type from <useragent>. It can be table,mobile,pc,tv or other.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.detect_useragent_device_type`("Mozilla/5.0 (iPad; CPU OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1")
```

**Example Output**:

```
tablet
```
---
## <a id='extract_url_path'></a>19. extract_url_path(url, clean_url_tail)

- **Type**: SQL
- **Tags**: new, text, URL, featured
- **Region**: us,eu
- **Description**: Extracts url path from <url>. Optionally remove url tail.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_path`(`url` STRING, `clean_url_tail` BOOL) 
  RETURNS STRING AS (CASE WHEN clean_url_tail THEN 
  SPLIT(SPLIT(url,NET.HOST(url))[SAFE_OFFSET(1)],'?')[SAFE_OFFSET(0)]
ELSE
  SPLIT(url,NET.HOST(url))[SAFE_OFFSET(1)]
END)
  OPTIONS ( description = '''Extracts url path from <url>. Optionally remove url tail.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_path`("https://hey.com/me/?parameter=1","True")
```

**Example Output**:

```
/me/
```
---
## <a id='extract_url_tail'></a>20. extract_url_tail(url)

- **Type**: SQL
- **Tags**: text, URL
- **Region**: us,eu
- **Description**: Extracts url tail from <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_tail`(`url` STRING) 
  RETURNS STRING AS (SPLIT(url,'?')[SAFE_OFFSET(1)])
  OPTIONS ( description = '''Extracts url tail from <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_tail`("https://hey.com/me/?parameter=1")
```

**Example Output**:

```
parameter=1
```
---
## <a id='extract_url_language'></a>21. extract_url_language(url)

- **Type**: SQL
- **Tags**: text, URL, new
- **Region**: us,eu
- **Description**: Extract language from a <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_url_language`(`url` STRING) 
  RETURNS STRING AS (CASE 
  -- North America
  WHEN REGEXP_CONTAINS(url, '/en(-[A-Za-z]{2})?/') THEN 'english'
  WHEN REGEXP_CONTAINS(url, '/es/') THEN 'spanish'

  -- Europe
  WHEN REGEXP_CONTAINS(url, '/fr/') THEN 'french'
  WHEN REGEXP_CONTAINS(url, '/de/') THEN 'german'
  WHEN REGEXP_CONTAINS(url, '/it/') THEN 'italian'
  WHEN REGEXP_CONTAINS(url, '/ru/') THEN 'russian'
  WHEN REGEXP_CONTAINS(url, '/pt-pt/') THEN 'portuguese'
  WHEN REGEXP_CONTAINS(url, '/el/') THEN 'greek'
  WHEN REGEXP_CONTAINS(url, '/sv-') THEN 'swedish'
  WHEN REGEXP_CONTAINS(url, '/pl/') THEN 'polish'
  WHEN REGEXP_CONTAINS(url, '/tr/') THEN 'turkish'
  WHEN REGEXP_CONTAINS(url, '/nl/') THEN 'dutch'
  WHEN REGEXP_CONTAINS(url, '/uk/') THEN 'ukrainian'
  WHEN REGEXP_CONTAINS(url, '/cs/') THEN 'czech'
  WHEN REGEXP_CONTAINS(url, '/da/') THEN 'danish'
  WHEN REGEXP_CONTAINS(url, '/fi/') THEN 'finnish'
  WHEN REGEXP_CONTAINS(url, '/hu/') THEN 'hungarian'
  WHEN REGEXP_CONTAINS(url, '/ro/') THEN 'romanian'
  WHEN REGEXP_CONTAINS(url, '/sk/') THEN 'slovak'
  WHEN REGEXP_CONTAINS(url, '/pt/') THEN 'portuguese'

  -- Asia
  WHEN REGEXP_CONTAINS(url, '/ar/') THEN 'arabic'
  WHEN REGEXP_CONTAINS(url, '/zh(-[A-Za-z]{2,5})?/') THEN 'chinese'
  WHEN REGEXP_CONTAINS(url, '/ja/') THEN 'japanese'
  WHEN REGEXP_CONTAINS(url, '/ko/') THEN 'korean'
  WHEN REGEXP_CONTAINS(url, '/hi/') THEN 'hindi'
  WHEN REGEXP_CONTAINS(url, '/ur/') THEN 'urdu'
  WHEN REGEXP_CONTAINS(url, '/bn/') THEN 'bengali'
  WHEN REGEXP_CONTAINS(url, '/fa/') THEN 'persian'
  WHEN REGEXP_CONTAINS(url, '/ta/') THEN 'tamil'
  WHEN REGEXP_CONTAINS(url, '/vi/') THEN 'vietnamese'
  WHEN REGEXP_CONTAINS(url, '/th/') THEN 'thai'
  WHEN REGEXP_CONTAINS(url, '/id/') THEN 'indonesian'
  WHEN REGEXP_CONTAINS(url, '/ms/') THEN 'malay'

  -- Africa
  WHEN REGEXP_CONTAINS(url, '/ar/') THEN 'arabic'  -- Arabic is also spoken widely in North Africa

  -- South America
  -- Spanish and Portuguese are majorly spoken here and are already added above

  -- Oceania
  -- English is a major language here and is already added above

  ELSE 'unknown'
END
)
  OPTIONS ( description = '''Extract language from a <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_url_language`("www.justdataplease.com/en-US/")
```

**Example Output**:

```
english
```
---
## <a id='extract_all_url_parameters'></a>22. extract_all_url_parameters(url)

- **Type**: JS
- **Tags**: text, URL, new
- **Region**: us,eu
- **Description**: Extracts all parameters from <url> in JSON format.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_all_url_parameters`(`url` STRING) RETURNS JSON
	LANGUAGE js AS r'''// Remove the fragment identifier (everything after '#')
var main_part = url.split('#')[0];

// Extract the query string part
var query_string = main_part.split('?')[1];
var params = query_string.split('&');
var obj = {};
for(var i = 0; i < params.length; i++) {
  var keyValue = params[i].split('=');
  obj[keyValue[0]] = keyValue[1];
}
return obj;
''' OPTIONS ( description = '''Extracts all parameters from <url> in JSON format.'''  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_all_url_parameters`("justdataplease.com/test/?medium=cpc&source=google&keyword=hey&source=facebook")
```

**Example Output**:

```
{"keyword":"hey","medium":"cpc","source":"facebook"}
```
---
## <a id='clean_email'></a>23. clean_email(email)

- **Type**: SQL
- **Tags**: text, email, featured
- **Region**: us,eu
- **Description**: Converts the <email> to lowercase and removes any sub-address (also known as plus addressing) if present.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.clean_email`(`email` STRING) 
  RETURNS STRING AS (LOWER(justfunctions.eu.remove_email_plus_address(email)))
  OPTIONS ( description = '''Converts the <email> to lowercase and removes any sub-address (also known as plus addressing) if present.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.clean_email`("HeLLo+other@gmail.com")
```

**Example Output**:

```
hello@gmail.com
```
---
## <a id='detect_free_email'></a>24. detect_free_email(email)

- **Type**: SQL
- **Tags**: text, email, new, featured
- **Region**: us,eu
- **Description**: Detects if <email> belongs to a free email service (gmail, yahoo, outlook, etc).

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.detect_free_email`(`email` STRING) 
  RETURNS INT AS (justfunctions.eu.detect_free_email_domain(
      justfunctions.eu.extract_url_domain_base(email)
))
  OPTIONS ( description = '''Detects if <email> belongs to a free email service (gmail, yahoo, outlook, etc).''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.detect_free_email`("jason@gmail.com")
```

**Example Output**:

```
1
```
---
## <a id='validate_email'></a>25. validate_email(email)

- **Type**: SQL
- **Tags**: text, email, new
- **Region**: us,eu
- **Description**: Detects if <email> is valid.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.validate_email`(`email` STRING) 
  RETURNS INT AS (CASE
   WHEN NET.REG_DOMAIN(lower(email)) IS NULL THEN 0
   WHEN REGEXP_CONTAINS(lower(email), "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])$") THEN 1
   ELSE 0
END
)
  OPTIONS ( description = '''Detects if <email> is valid.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.validate_email`("12/jason@gmail.com")
```

**Example Output**:

```
0
```
---
## <a id='decode_url'></a>26. decode_url(url)

- **Type**: SQL
- **Tags**: text, url
- **Region**: us,eu
- **Description**: Decodes <url>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.decode_url`(`url` STRING) 
  RETURNS STRING AS (((
  SELECT STRING_AGG(
    IF(REGEXP_CONTAINS(y, r'^%[0-9a-fA-F]{2}'), 
      SAFE_CONVERT_BYTES_TO_STRING(FROM_HEX(REPLACE(y, '%', ''))), y), '' 
    ORDER BY i
    )
  FROM UNNEST(REGEXP_EXTRACT_ALL(url, r"%[0-9a-fA-F]{2}(?:%[0-9a-fA-F]{2})*|[^%]+")) y
  WITH OFFSET AS i 
)))
  OPTIONS ( description = '''Decodes <url>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.decode_url`("https%3A%2F%2Fjustdataplease.com%2Fjustfunctions-bigquery%2F%3Futm_campaign%3Dtest")
```

**Example Output**:

```
https://justdataplease.com/justfunctions-bigquery/?utm_campaign=test
```
---
## <a id='dedup_chars'></a>27. dedup_chars(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Deduplicate characters in 'string`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.dedup_chars`(`string` string) 
  RETURNS string AS ((SELECT
STRING_AGG(
  IF
    (c = SPLIT(string, '')[SAFE_OFFSET(off - 1)],
      NULL,
      c), '' ORDER BY off)
FROM
UNNEST(SPLIT(string, '')) AS c
WITH OFFSET off)
)
  OPTIONS ( description = '''Deduplicate characters in 'string`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.dedup_chars`("Helloooo!")
```

**Example Output**:

```
Helo!
```
---
## <a id='word_tokens'></a>28. word_tokens(string, symbol)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Splits 'string' into words.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.word_tokens`(`string` string, `symbol` string) 
  RETURNS ARRAY<STRING> AS (SPLIT(REGEXP_REPLACE(LOWER(string),symbol," "), " "))
  OPTIONS ( description = '''Splits 'string' into words.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.word_tokens`("this is a sentence","\\s+")
```

**Example Output**:

```
['this', 'is', 'a', 'sentence']
```
---
## <a id='replace_urls'></a>29. replace_urls(string, replacement)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Replace url patterns in a `string` with `replacement`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.replace_urls`(`string` string, `replacement` string) 
  RETURNS string AS (REGEXP_REPLACE(string, r'((ftp|https?)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z0-9\&\.\!\%\/\?\:@\-_=#])*', replacement))
  OPTIONS ( description = '''Replace url patterns in a `string` with `replacement`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.replace_urls`("Google it https://www.google.com/ !","")
```

**Example Output**:

```
Google it !
```
---
## <a id='stemmer_greek'></a>30. stemmer_greek(string)

- **Type**: JS
- **Tags**: NLP, text, stemmer
- **Region**: us,eu
- **Description**: Returns the stem of the `string`. Supports Greek Language.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.stemmer_greek`(`string` string) RETURNS string
	LANGUAGE js AS r'''return utils.greekStemmer(string.toUpperCase());''' OPTIONS ( description = '''Returns the stem of the `string`. Supports Greek Language.'''  , library = [  "gs://justfunctions/bigquery-functions/stemmers.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.stemmer_greek`("καλησπερα")
```

**Example Output**:

```
ΚΑΛΗΣΠΕΡ
```
---
## <a id='normalize_text'></a>31. normalize_text(string)

- **Type**: SQL
- **Tags**: NLP, text, new, featured
- **Region**: us,eu
- **Description**: Normalize given <string> by converting it to lowercase, applying transliteration, removing special characters and extra spaces.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.normalize_text`(`string` string) 
  RETURNS string AS (TRIM(
  justfunctions.eu.remove_extra_whitespaces(
      justfunctions.eu.transliterate_anyascii(
            justfunctions.eu.clean_special_symbols(
                  LOWER(
                    string
                  )
            )
      )
  )
))
  OPTIONS ( description = '''Normalize given <string> by converting it to lowercase, applying transliteration, removing special characters and extra spaces.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.normalize_text`("🎉 Welcome to Athens in 2023! Καλώς ήρθες!")
```

**Example Output**:

```
welcome to athens in 2023
```
---
## <a id='remove_accents'></a>32. remove_accents(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Remove accents from `string`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.remove_accents`(`string` string) 
  RETURNS string AS (regexp_replace(normalize(string, nfd), r"\pm", ''))
  OPTIONS ( description = '''Remove accents from `string`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.remove_accents`("¿Dóndé Éstá Mí Ágúá?")
```

**Example Output**:

```
¿Donde Esta Mi Agua?
```
---
## <a id='stemmer_porter'></a>33. stemmer_porter(string)

- **Type**: JS
- **Tags**: NLP, text, stemmer
- **Region**: us,eu
- **Description**: Returns the stem of the `string`, using Porter Algorythm. Supports English Language.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.stemmer_porter`(`string` string) RETURNS string
	LANGUAGE js AS r'''return utils.porterStemmer(string);''' OPTIONS ( description = '''Returns the stem of the `string`, using Porter Algorythm. Supports English Language.'''  , library = [  "gs://justfunctions/bigquery-functions/stemmers.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.stemmer_porter`("replied")
```

**Example Output**:

```
repli
```
---
## <a id='replace_html_tags'></a>34. replace_html_tags(string, replacement)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Replace html tags in a `string` with `replacement`

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.replace_html_tags`(`string` string, `replacement` string) 
  RETURNS string AS (TRIM(REGEXP_REPLACE(string, r"<[^>]*>", replacement)))
  OPTIONS ( description = '''Replace html tags in a `string` with `replacement`''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.replace_html_tags`("<div class=\'test\'>hello world<a href=\'#\'>hello world<\a><\\div>"," ")
```

**Example Output**:

```
hello world hello world
```
---
## <a id='stemmer_lancaster'></a>35. stemmer_lancaster(string)

- **Type**: JS
- **Tags**: NLP, text, stemmer
- **Region**: us,eu
- **Description**: Returns the stem of the `string`, using Lancaster Algorythm. Supports English Language.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.stemmer_lancaster`(`string` string) RETURNS string
	LANGUAGE js AS r'''return utils.lancasterStemmer(string);''' OPTIONS ( description = '''Returns the stem of the `string`, using Lancaster Algorythm. Supports English Language.'''  , library = [  "gs://justfunctions/bigquery-functions/stemmers.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.stemmer_lancaster`("replied")
```

**Example Output**:

```
reply
```
---
## <a id='remove_en_stopwords'></a>36. remove_en_stopwords(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Remove english stopwords from `string`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.remove_en_stopwords`(`string` string) 
  RETURNS string AS (REGEXP_REPLACE(LOWER(string),r"\ba\b|\babout\b|\babove\b|\bafter\b|\bagain\b|\bagainst\b|\ball\b|\bam\b|\ban\b|\band\b|\bany\b|\bare\b|\baren't\b|\bas\b|\bat\b|\bbe\b|\bbecause\b|\bbeen\b|\bbefore\b|\bbeing\b|\bbelow\b|\bbetween\b|\bboth\b|\bbut\b|\bby\b|\bcan't\b|\bcannot\b|\bcould\b|\bcouldn't\b|\bdid\b|\bdidn't\b|\bdo\b|\bdoes\b|\bdoesn't\b|\bdoing\b|\bdon't\b|\bdown\b|\bduring\b|\beach\b|\bfew\b|\bfor\b|\bfrom\b|\bfurther\b|\bhad\b|\bhadn't\b|\bhas\b|\bhasn't\b|\bhave\b|\bhaven't\b|\bhaving\b|\bhe\b|\bhe'd\b|\bhe'll\b|\bhe's\b|\bher\b|\bhere\b|\bhere's\b|\bhers\b|\bherself\b|\bhim\b|\bhimself\b|\bhis\b|\bhow\b|\bhow's\b|\bi\b|\bi'd\b|\bi'll\b|\bi'm\b|\bi've\b|\bif\b|\bin\b|\binto\b|\bis\b|\bisn't\b|\bit\b|\bit's\b|\bits\b|\bitself\b|\blet's\b|\bme\b|\bmore\b|\bmost\b|\bmustn't\b|\bmy\b|\bmyself\b|\bno\b|\bnor\b|\bnot\b|\bof\b|\boff\b|\bon\b|\bonce\b|\bonly\b|\bor\b|\bother\b|\bought\b|\bour\b|\bours\b|\bourselves\b|\bout\b|\bover\b|\bown\b|\bsame\b|\bshan't\b|\bshe\b|\bshe'd\b|\bshe'll\b|\bshe's\b|\bshould\b|\bshouldn't\b|\bso\b|\bsome\b|\bsuch\b|\bthan\b|\bthat\b|\bthat's\b|\bthe\b|\btheir\b|\btheirs\b|\bthem\b|\bthemselves\b|\bthen\b|\bthere\b|\bthere's\b|\bthese\b|\bthey\b|\bthey'd\b|\bthey'll\b|\bthey're\b|\bthey've\b|\bthis\b|\bthose\b|\bthrough\b|\bto\b|\btoo\b|\bunder\b|\buntil\b|\bup\b|\bvery\b|\bwas\b|\bwasn't\b|\bwe\b|\bwe'd\b|\bwe'll\b|\bwe're\b|\bwe've\b|\bwere\b|\bweren't\b|\bwhat\b|\bwhat's\b|\bwhen\b|\bwhen's\b|\bwhere\b|\bwhere's\b|\bwhich\b|\bwhile\b|\bwho\b|\bwho's\b|\bwhom\b|\bwhy\b|\bwhy's\b|\bwith\b|\bwon't\b|\bwould\b|\bwouldn't\b|\byou\b|\byou'd\b|\byou'll\b|\byou're\b|\byou've\b|\byour\b|\byours\b|\byourself\b|\byourselves\b",''))
  OPTIONS ( description = '''Remove english stopwords from `string`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.remove_en_stopwords`("The query in the database is returning the rows with the specified column values.")
```

**Example Output**:

```
query   database  returning  rows   specified column values.
```
---
## <a id='remove_extra_spaces'></a>37. remove_extra_spaces(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Remove extra spaces (tap,space,newline,paragraph etc) in a `string`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.remove_extra_spaces`(`string` string) 
  RETURNS string AS (TRIM(REGEXP_REPLACE(REGEXP_REPLACE(string,r'\n+|\t+|\r+|\\n+|\\t+|\\r+|\\s+',''), r'\s+', ' ')))
  OPTIONS ( description = '''Remove extra spaces (tap,space,newline,paragraph etc) in a `string`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.remove_extra_spaces`("\tHi     there
.\n\n")
```

**Example Output**:

```
Hi there.
```
---
## <a id='extract_email_domain'></a>38. extract_email_domain(url)

- **Type**: SQL
- **Tags**: text, email
- **Region**: us,eu
- **Description**: Extract the domain of an <email>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_email_domain`(`url` STRING) 
  RETURNS STRING AS (NET.REG_DOMAIN(url))
  OPTIONS ( description = '''Extract the domain of an <email>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_email_domain`("jason@justdataplease.com")
```

**Example Output**:

```
justdataplease.com
```
---
## <a id='clean_special_symbols'></a>39. clean_special_symbols(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Clean special symbols in a `string` using custom symbols.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.clean_special_symbols`(`string` string) 
  RETURNS string AS (REGEXP_REPLACE(string, '''[^\\p{L}\\p{N}\\s]+''', ''))
  OPTIONS ( description = '''Clean special symbols in a `string` using custom symbols.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.clean_special_symbols`("Vacation✈️ time!🌴😀🏖️")
```

**Example Output**:

```
vacation time
```
---
## <a id='transliterate_anyascii'></a>40. transliterate_anyascii(string)

- **Type**: JS
- **Tags**: NLP, text, transliteration
- **Region**: us,eu
- **Description**: Converts Unicode characters to their best ASCII representation.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.transliterate_anyascii`(`string` string) RETURNS string
	LANGUAGE js AS r'''return utils.anyAscii(string);''' OPTIONS ( description = '''Converts Unicode characters to their best ASCII representation.'''  , library = [  "gs://justfunctions/bigquery-functions/transliteration.js" ]  )
```
**Example Query**:

```sql
SELECT `justfunctions.eu.transliterate_anyascii`("καλημέρα")
```

**Example Output**:

```
kalimera
```
---
## <a id='replace_en_contractions'></a>41. replace_en_contractions(string, replacement)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Replace english contractions in 'string'.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.replace_en_contractions`(`string` string, `replacement` string) 
  RETURNS string AS ((WITH 
words AS (SELECT * FROM unnest(SPLIT(REGEXP_REPLACE(LOWER(string),replacement," "), " ")) as word),

list AS (SELECT LOWER(JSON_EXTRACT_SCALAR(c,"$.key")) key_part,LOWER(JSON_EXTRACT_SCALAR(c,"$.value")) value_part  FROM
unnest([
'{"key":"I\'m","value":"I am"}',
'{"key":"I\'m\'a","value":"I am about to"}',
'{"key":"I\'m\'o","value":"I am going to"}',
'{"key":"I\'ve","value":"I have"}',
'{"key":"I\'ll","value":"I will"}',
'{"key":"I\'ll\'ve","value":"I will have"}',
'{"key":"I\'d","value":"I would"}',
'{"key":"I\'d\'ve","value":"I would have"}',
'{"key":"Whatcha","value":"What are you"}',
'{"key":"amn\'t","value":"am not"}',
'{"key":"ain\'t","value":"are not"}',
'{"key":"aren\'t","value":"are not"}',
'{"key":"\'cause","value":"because"}',
'{"key":"can\'t","value":"cannot"}',
'{"key":"can\'t\'ve","value":"cannot have"}',
'{"key":"could\'ve","value":"could have"}',
'{"key":"couldn\'t","value":"could not"}',
'{"key":"couldn\'t\'ve","value":"could not have"}',
'{"key":"daren\'t","value":"dare not"}',
'{"key":"daresn\'t","value":"dare not"}',
'{"key":"dasn\'t","value":"dare not"}',
'{"key":"didn\'t","value":"did not"}',
'{"key":"didn’t","value":"did not"}',
'{"key":"don\'t","value":"do not"}',
'{"key":"don’t","value":"do not"}',
'{"key":"doesn\'t","value":"does not"}',
'{"key":"e\'er","value":"ever"}',
'{"key":"everyone\'s","value":"everyone is"}',
'{"key":"finna","value":"fixing to"}',
'{"key":"gimme","value":"give me"}',
'{"key":"gon\'t","value":"go not"}',
'{"key":"gonna","value":"going to"}',
'{"key":"gotta","value":"got to"}',
'{"key":"hadn\'t","value":"had not"}',
'{"key":"hadn\'t\'ve","value":"had not have"}',
'{"key":"hasn\'t","value":"has not"}',
'{"key":"haven\'t","value":"have not"}',
'{"key":"he\'ve","value":"he have"}',
'{"key":"he\'s","value":"he is"}',
'{"key":"he\'ll","value":"he will"}',
'{"key":"he\'ll\'ve","value":"he will have"}',
'{"key":"he\'d","value":"he would"}',
'{"key":"he\'d\'ve","value":"he would have"}',
'{"key":"here\'s","value":"here is"}',
'{"key":"how\'re","value":"how are"}',
'{"key":"how\'d","value":"how did"}',
'{"key":"how\'d\'y","value":"how do you"}',
'{"key":"how\'s","value":"how is"}',
'{"key":"how\'ll","value":"how will"}',
'{"key":"isn\'t","value":"is not"}',
'{"key":"it\'s","value":"it is"}',
'{"key":"\'tis","value":"it is"}',
'{"key":"\'twas","value":"it was"}',
'{"key":"it\'ll","value":"it will"}',
'{"key":"it\'ll\'ve","value":"it will have"}',
'{"key":"it\'d","value":"it would"}',
'{"key":"it\'d\'ve","value":"it would have"}',
'{"key":"kinda","value":"kind of"}',
'{"key":"let\'s","value":"let us"}',
'{"key":"luv","value":"love"}',
'{"key":"ma\'am","value":"madam"}',
'{"key":"may\'ve","value":"may have"}',
'{"key":"mayn\'t","value":"may not"}',
'{"key":"might\'ve","value":"might have"}',
'{"key":"mightn\'t","value":"might not"}',
'{"key":"mightn\'t\'ve","value":"might not have"}',
'{"key":"must\'ve","value":"must have"}',
'{"key":"mustn\'t","value":"must not"}',
'{"key":"mustn\'t\'ve","value":"must not have"}',
'{"key":"needn\'t","value":"need not"}',
'{"key":"needn\'t\'ve","value":"need not have"}',
'{"key":"ne\'er","value":"never"}',
'{"key":"o\'","value":"of"}',
'{"key":"o\'clock","value":"of the clock"}',
'{"key":"ol\'","value":"old"}',
'{"key":"oughtn\'t","value":"ought not"}',
'{"key":"oughtn\'t\'ve","value":"ought not have"}',
'{"key":"o\'er","value":"over"}',
'{"key":"shan\'t","value":"shall not"}',
'{"key":"sha\'n\'t","value":"shall not"}',
'{"key":"shalln\'t","value":"shall not"}',
'{"key":"shan\'t\'ve","value":"shall not have"}',
'{"key":"she\'s","value":"she is"}',
'{"key":"she\'ll","value":"she will"}',
'{"key":"she\'d","value":"she would"}',
'{"key":"she\'d\'ve","value":"she would have"}',
'{"key":"should\'ve","value":"should have"}',
'{"key":"shouldn\'t","value":"should not"}',
'{"key":"shouldn\'t\'ve","value":"should not have"}',
'{"key":"so\'ve","value":"so have"}',
'{"key":"so\'s","value":"so is"}',
'{"key":"somebody\'s","value":"somebody is"}',
'{"key":"someone\'s","value":"someone is"}',
'{"key":"something\'s","value":"something is"}',
'{"key":"sux","value":"sucks"}',
'{"key":"that\'re","value":"that are"}',
'{"key":"that\'s","value":"that is"}',
'{"key":"that\'ll","value":"that will"}',
'{"key":"that\'d","value":"that would"}',
'{"key":"that\'d\'ve","value":"that would have"}',
'{"key":"\'em","value":" them"}',
'{"key":"there\'re","value":"there are"}',
'{"key":"there\'s","value":"there is"}',
'{"key":"there\'ll","value":"there will"}',
'{"key":"there\'d","value":"there would"}',
'{"key":"there\'d\'ve","value":"there would have"}',
'{"key":"these\'re","value":"these are"}',
'{"key":"they\'re","value":"they are"}',
'{"key":"they\'ve","value":"they have"}',
'{"key":"they\'ll","value":"they will"}',
'{"key":"they\'ll\'ve","value":"they will have"}',
'{"key":"they\'d","value":"they would"}',
'{"key":"they\'d\'ve","value":"they would have"}',
'{"key":"this\'s","value":"this is"}',
'{"key":"this\'ll","value":"this will"}',
'{"key":"this\'d","value":"this would"}',
'{"key":"those\'re","value":"those are"}',
'{"key":"to\'ve","value":"to have"}',
'{"key":"wanna","value":"want to"}',
'{"key":"wasn\'t","value":"was not"}',
'{"key":"we\'re","value":"we are"}',
'{"key":"we\'ve","value":"we have"}',
'{"key":"we\'ll","value":"we will"}',
'{"key":"we\'ll\'ve","value":"we will have"}',
'{"key":"we\'d","value":"we would"}',
'{"key":"we\'d\'ve","value":"we would have"}',
'{"key":"weren\'t","value":"were not"}',
'{"key":"what\'re","value":"what are"}',
'{"key":"what\'d","value":"what did"}',
'{"key":"what\'ve","value":"what have"}',
'{"key":"what\'s","value":"what is"}',
'{"key":"what\'ll","value":"what will"}',
'{"key":"what\'ll\'ve","value":"what will have"}',
'{"key":"when\'ve","value":"when have"}',
'{"key":"when\'s","value":"when is"}',
'{"key":"where\'re","value":"where are"}',
'{"key":"where\'d","value":"where did"}',
'{"key":"where\'ve","value":"where have"}',
'{"key":"where\'s","value":"where is"}',
'{"key":"which\'s","value":"which is"}',
'{"key":"who\'re","value":"who are"}',
'{"key":"who\'ve","value":"who have"}',
'{"key":"who\'s","value":"who is"}',
'{"key":"who\'ll","value":"who will"}',
'{"key":"who\'ll\'ve","value":"who will have"}',
'{"key":"who\'d","value":"who would"}',
'{"key":"who\'d\'ve","value":"who would have"}',
'{"key":"why\'re","value":"why are"}',
'{"key":"why\'d","value":"why did"}',
'{"key":"why\'ve","value":"why have"}',
'{"key":"why\'s","value":"why is"}',
'{"key":"will\'ve","value":"will have"}',
'{"key":"won\'t","value":"will not"}',
'{"key":"won\'t\'ve","value":"will not have"}',
'{"key":"would\'ve","value":"would have"}',
'{"key":"wouldn\'t","value":"would not"}',
'{"key":"wouldn\'t\'ve","value":"would not have"}',
'{"key":"y\'all","value":"you all"}',
'{"key":"y\'all\'re","value":"you all are"}',
'{"key":"y\'all\'ve","value":"you all have"}',
'{"key":"y\'all\'d","value":"you all would"}',
'{"key":"y\'all\'d\'ve","value":"you all would have"}',
'{"key":"you\'re","value":"you are"}',
'{"key":"you\'ve","value":"you have"}',
'{"key":"you\'ll\'ve","value":"you shall have"}',
'{"key":"you\'ll","value":"you will"}',
'{"key":"you\'d","value":"you would"}',
'{"key":"you\'d\'ve","value":"you would have"}',
'{"key":"\'aight","value":"alright"}',
'{"key":"abt","value":"about"}',
'{"key":"acct","value":"account"}',
'{"key":"altho","value":"although"}',
'{"key":"asap","value":"as soon as possible"}',
'{"key":"avg","value":"average"}',
'{"key":"b4","value":"before"}',
'{"key":"bc","value":"because"}',
'{"key":"bday","value":"birthday"}',
'{"key":"btw","value":"by the way"}',
'{"key":"convo","value":"conversation"}',
'{"key":"cya","value":"see ya"}',
'{"key":"diff","value":"different"}',
'{"key":"dunno","value":"do not know"}',
'{"key":"g\'day","value":"good day"}',
'{"key":"howdy","value":"how do you do"}',
'{"key":"idk","value":"I do not know"}',
'{"key":"ima","value":"I am going to"}',
'{"key":"imma","value":"I am going to"}',
'{"key":"innit","value":"is it not"}',
'{"key":"iunno","value":"I do not know"}',
'{"key":"kk","value":"okay"}',
'{"key":"lemme","value":"let me"}',
'{"key":"msg","value":"message"}',
'{"key":"nvm","value":"nevermind"}',
'{"key":"ofc","value":"of course"}',
'{"key":"ppl","value":"people"}',
'{"key":"prolly","value":"probably"}',
'{"key":"pymnt","value":"payment"}',
'{"key":"r ","value":"are "}',
'{"key":"rlly","value":"really"}',
'{"key":"rly","value":"really"}',
'{"key":"rn","value":"right now"}',
'{"key":"spk","value":"spoke"}',
'{"key":"tbh","value":"to be honest"}',
'{"key":"tho","value":"though"}',
'{"key":"thx","value":"thanks"}',
'{"key":"tlked","value":"talked"}',
'{"key":"tmmw","value":"tomorrow"}',
'{"key":"tmr","value":"tomorrow"}',
'{"key":"tmrw","value":"tomorrow"}',
'{"key":"u","value":"you"}',
'{"key":"ur","value":"you are"}',
'{"key":"woulda","value":"would have"}',
'{"key":"\'all","value":""}',
'{"key":"\'am","value":""}',
'{"key":"\'d","value":" would"}',
'{"key":"\'ll","value":" will"}',
'{"key":"\'re","value":" are"}',
'{"key":"doin\'","value":"doing"}',
'{"key":"goin\'","value":"going"}',
'{"key":"nothin\'","value":"nothing"}',
'{"key":"somethin\'","value":"something"}',
'{"key":"havin\'","value":"having"}',
'{"key":"lovin\'","value":"loving"}',
'{"key":"\'coz","value":"because"}',
'{"key":"thats","value":"that is"}',
'{"key":"whats","value":"what is"}']) as c)
SELECT string_agg(CASE WHEN value_part IS NOT NULL THEN value_part ELSE word END," ") final  FROM words LEFT JOIN list ON list.key_part=words.word
)
)
  OPTIONS ( description = '''Replace english contractions in 'string'.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.replace_en_contractions`("I'll be great tmr thx","r"\s+"")
```

**Example Output**:

```
I will be great tomorrow thanks
```
---
## <a id='remove_extra_whitespaces'></a>42. remove_extra_whitespaces(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Remove extra whitespaces in a `string`.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.remove_extra_whitespaces`(`string` string) 
  RETURNS string AS (REGEXP_REPLACE(string, r'\s+',' '))
  OPTIONS ( description = '''Remove extra whitespaces in a `string`.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.remove_extra_whitespaces`("Hi     there
.")
```

**Example Output**:

```
Hi there
.
```
---
## <a id='extract_email_domain_base'></a>43. extract_email_domain_base(url)

- **Type**: SQL
- **Tags**: text, email
- **Region**: us,eu
- **Description**: Extract the domain base of an <email>.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.extract_email_domain_base`(`url` STRING) 
  RETURNS STRING AS (REPLACE (NET.REG_DOMAIN(url), CONCAT('.',NET.PUBLIC_SUFFIX(url)),""))
  OPTIONS ( description = '''Extract the domain base of an <email>.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.extract_email_domain_base`("jason@justdataplease.com")
```

**Example Output**:

```
justdataplease
```
---
## <a id='clean_special_symbols_custom'></a>44. clean_special_symbols_custom(string)

- **Type**: SQL
- **Tags**: NLP, text
- **Region**: us,eu
- **Description**: Clean special symbols in a `string` using custom symbols.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.clean_special_symbols_custom`(`string` string) 
  RETURNS string AS (REGEXP_REPLACE(string, r'[\'♥◄£⌠Æ`╥&è°Üε\^Ÿü▄¡↓\]▲¢>|Î¸.•¤→│®;…Œ§´ï›Ä√ß╝♪Ì℃Ò¨˜ò©à/┼≡"ÂÑ♠∟ƒ@▓ÕôÍⁿ┴╣“ž↔―╢╞\?™╤ð}¦—‡„╠³óÞ℉ÿ∙∩▀↨╫╒ÊÓù║<ÈÏ☺±╬▌â╪╘┘$Ë╓█÷Ý≤Ž╟#≥þÇ\(╨·\*⌡š†⌂œØ↕€♂╦’ã╖╔ÐÅ■ê”ú┬‼ç¿▒ª┌äÛ╕ÉÔºö♦ñÀ♀├↑╗ì\\╧♫╡○└Öý-←╚╩♣Ã¥å¬¯‰\[ˆû≈₧Š►▐∞!Ù,²▬î╛=×┐\:–─═‘◘é\+◙\)‹_Á{░Ú¹⌐ë»‚☼%╙▼~⊙á\'õø¶☻«┤æí]+', ''))
  OPTIONS ( description = '''Clean special symbols in a `string` using custom symbols.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.clean_special_symbols_custom`("Vacation✈️ time!🌴😀🏖️")
```

**Example Output**:

```
vacation time
```
---
## <a id='dedup_table'></a>45. dedup_table(table_name, timestamp_column, unique_column, output_table_suffix)

- **Type**: PROCEDURE
- **Tags**: Operations, new, featured
- **Region**: us,eu
- **Description**: Creates a deduplicated version of <table>. It keeps the chronologically (`timestamp_column`) latest row of the `unique column` or uses other methods based on arguments availability. Arguments `timestamp_column`, `unique_column`, `output_table_suffix` are optional.

```sql
CREATE OR REPLACE PROCEDURE `justfunctions.eu.dedup_table`(`table_name` string, `timestamp_column` string, `unique_column` string, `output_table_suffix` string)
options(
    description = '''Creates a deduplicated version of <table>. It keeps the chronologically (`timestamp_column`) latest row of the `unique column` or uses other methods based on arguments availability. Arguments `timestamp_column`, `unique_column`, `output_table_suffix` are optional.'''
)
BEGIN

DECLARE sql STRING;
DECLARE final_table_name STRING;

SET final_table_name = CONCAT(table_name, IF(output_table_suffix != '', output_table_suffix, '_dedup'));

IF unique_column = '' AND timestamp_column = '' THEN
  SET sql = FORMAT("""
    CREATE OR REPLACE TABLE %s AS
    SELECT DISTINCT *
    FROM %s;
  """, final_table_name, table_name);
ELSEIF unique_column != '' AND timestamp_column = '' THEN
  SET sql = FORMAT("""
    CREATE OR REPLACE TABLE %s AS
    SELECT * EXCEPT(row_num)
    FROM (
      SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY %s) AS row_num
      FROM
        %s
    )
    WHERE row_num = 1;
  """, final_table_name, unique_column, table_name);
ELSE
  SET sql = FORMAT("""
    CREATE OR REPLACE TABLE %s AS
    SELECT * EXCEPT(row_num)
    FROM (
      SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY %s ORDER BY %s DESC) AS row_num
      FROM
        %s
    )
    WHERE row_num = 1;
  """, final_table_name, unique_column, timestamp_column, table_name);
END IF;

EXECUTE IMMEDIATE sql;


END;
```
**Example Query**:

```sql
CALL `justfunctions.eu.dedup_table`("your_project.your_dataset.your_table","created_at","user_id","_dedup")
```

**Example Output**:

```
your_project.your_dataset.your_table.your_table_dedup
```
---
## <a id='generate_justsql_schema'></a>46. generate_justsql_schema(project_id, dataset_id, tables)

- **Type**: PROCEDURE
- **Tags**: Operations, new, featured
- **Region**: us,eu
- **Description**: Generates a json_schema to use with JustSQL GPT (https://chat.openai.com/g/g-hzlGYume7-justsql-for-bigquery).

```sql
CREATE OR REPLACE PROCEDURE `justfunctions.eu.generate_justsql_schema`(`project_id` string, `dataset_id` string, `tables` array<string>)
options(
    description = '''Generates a json_schema to use with JustSQL GPT (https://chat.openai.com/g/g-hzlGYume7-justsql-for-bigquery).'''
)
BEGIN

DECLARE query_string STRING;
DECLARE json_schema STRING DEFAULT '';
DECLARE tables_string STRING;

SET tables_string = ARRAY_TO_STRING(ARRAY(SELECT '\'' || x || '\'' FROM UNNEST(tables) AS x), ',');

SET query_string = CONCAT(
  'SELECT ',
  'CONCAT(\'{ "tables": [\', STRING_AGG(table_schema_, \',\' ORDER BY table_name), \'] }\' ) AS json_schema ',
  'FROM (  SELECT  table_name,table_schema,table_catalog,',
  'CONCAT(\'{ "table_name": "\', CONCAT(table_catalog,\'.\',table_schema,\'.\',table_name), \'", "columns": [\', STRING_AGG(CONCAT(\'{ "name": "\',column_name,\'","type":"\',data_type,\'"}\'), \',\'),\'] }\') AS table_schema_ ',
  'FROM \`',project_id,'.',dataset_id,'.INFORMATION_SCHEMA.COLUMNS\` ',
  'WHERE table_name IN (', tables_string, ') ',
  'GROUP BY 1,2,3 ) A'
);

EXECUTE IMMEDIATE query_string INTO json_schema;
SELECT json_schema;


END;
```
**Example Query**:

```sql
CALL `justfunctions.eu.generate_justsql_schema`("justfunctions","searchconsole","searchdata_site_impression")
```

**Example Output**:

```
{ "tables": [{ "table_name": "searchdata_site_impression", "columns": [{ "name": "data_date","type":"DATE"},{ "name": "site_url","type":"STRING"},{ "name": "query","type":"STRING"},{ "name": "country","type":"STRING"},{ "name": "device","type":"STRING"},{ "name": "impressions","type":"INT64"},{ "name": "clicks","type":"INT64"}] }
```
---
## <a id='percentile'></a>47. percentile(arr, percentile)

- **Type**: SQL
- **Tags**: STATISTICS, percentile
- **Region**: us,eu
- **Description**: Find percentile of 'array'.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.percentile`(`arr` array<float64>, `percentile` int) 
  RETURNS float64 AS ((
SELECT
COALESCE(arr[SAFE_OFFSET(CAST(ARRAY_LENGTH(arr)*percentile/100 AS INT)-1)],COALESCE(arr[SAFE_OFFSET (0)],999))
FROM (SELECT ARRAY_AGG(x IGNORE NULLS ORDER BY x) AS arr FROM UNNEST(arr) AS x)
)
)
  OPTIONS ( description = '''Find percentile of 'array'.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.percentile`("[1.2, 2.3, 3.2, 4.2, 5]")
```

**Example Output**:

```
3.2
```
---
## <a id='seconds_to_date'></a>48. seconds_to_date(seconds)

- **Type**: SQL
- **Tags**: date
- **Region**: us,eu
- **Description**: Converts the <seconds> to date format '%Y-%m-%d'.

```sql
CREATE OR REPLACE FUNCTION `justfunctions.eu.seconds_to_date`(`seconds` INT64) 
  RETURNS DATE AS (DATE(FORMAT_DATE('%Y-%m-%d',TIMESTAMP_SECONDS(seconds))))
  OPTIONS ( description = '''Converts the <seconds> to date format '%Y-%m-%d'.''')
```
**Example Query**:

```sql
SELECT `justfunctions.eu.seconds_to_date`("1687613655")
```

**Example Output**:

```
2023-06-24
```
---
