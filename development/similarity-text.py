import hashlib
import Levenshtein

from nltk.util import ngrams
from nltk.metrics.distance import jaccard_distance

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from terec.database import cassandra_session
from terec.model.util import cqlengine_init
from terec.model.results import TestCaseRun

# initialize cassandra connection
cassandra = cassandra_session()
cqlengine_init(cassandra)


# Failure = namedtuple('Failure', ['stdout', 'stderr', 'error_details', 'error_stacktrace'])

# view_filtering_test_timeout_stacktrace = "junit.framework.AssertionFailedError: Timeout occurred. Please note the time in the report does not reflect the time until the timeout.\n\tat java.util.Vector.forEach(Vector.java:1277)\n\tat java.util.Vector.forEach(Vector.java:1277)\n\tat java.util.Vector.forEach(Vector.java:1277)\n\tat jdk.nashorn.internal.scripts.Script$4$\^eval\_.:program(<eval>:13)\n\tat jdk.nashorn.internal.runtime.ScriptFunctionData.invoke(ScriptFunctionData.java:637)\n\tat jdk.nashorn.internal.runtime.ScriptFunction.invoke(ScriptFunction.java:494)\n\tat jdk.nashorn.internal.runtime.ScriptRuntime.apply(ScriptRuntime.java:393)\n\tat jdk.nashorn.api.scripting.NashornScriptEngine.evalImpl(NashornScriptEngine.java:449)\n\tat jdk.nashorn.api.scripting.NashornScriptEngine.evalImpl(NashornScriptEngine.java:406)\n\tat jdk.nashorn.api.scripting.NashornScriptEngine.evalImpl(NashornScriptEngine.java:402)\n\tat jdk.nashorn.api.scripting.NashornScriptEngine.eval(NashornScriptEngine.java:155)\n\tat javax.script.AbstractScriptEngine.eval(AbstractScriptEngine.java:264)\n\tat java.util.Vector.forEach(Vector.java:1277)\n"
# view_filtering_test_timeout_error = "Timeout occurred. Please note the time in the report does not reflect the time until the timeout."

# similar_server_timeout {
#     "All host(s) tried for query failed (tried: localhost/127.0.0.1:45337 (com.datastax.driver.core.exceptions.OperationTimedOutException: [localhost/127.0.0.1] Timed out waiting for server response))",
#     "All host(s) tried for query failed (tried: localhost/127.0.0.1:42777 (com.datastax.driver.core.exceptions.OperationTimedOutException: [localhost/127.0.0.1] Timed out waiting for server response))"
# }

org = "apache"
project = "cassandra"
suite = "cassandra-3.11-ci"
test_package = "org.apache.cassandra.cql3"
test_suite = "ViewComplexTest"

failed_tests = (
    TestCaseRun.objects()
    .filter(
        org=org,
        project=project,
        suite=suite,
        test_package=test_package,
        test_suite=test_suite,
        result="FAIL",
    )
    .allow_filtering()
    .all()
)

print(f"Found {len(failed_tests)} failed tests")


def levenshtein_similarity_ratio(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    normalized_distance = distance / max(len(str1), len(str2))
    similarity_ratio = 1 - normalized_distance
    return similarity_ratio


def jaccard_ngram_similarity(str1, str2, n):
    ngrams_str1 = set(ngrams(str1, n))
    ngrams_str2 = set(ngrams(str2, n))
    # Jaccard distance is used for similarity calculation
    jaccard_similarity = 1 - jaccard_distance(ngrams_str1, ngrams_str2)
    return jaccard_similarity


def cosine_sim(str1, str2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([str1.lower(), str2.lower()])
    # Compute cosine similarity between documents
    cosine_similarity_matrix = cosine_similarity(tfidf_matrix)
    # Extract the similarity score from the matrix
    cosine_similarity_score = cosine_similarity_matrix[0, 1]
    # Normalize to obtain similarity ratio in the range of 0 to 1
    return (cosine_similarity_score + 1) / 2


def generate_sha256(input_string):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()
    # Update the hash object with the bytes-like object of the input string
    sha256_hash.update(input_string.encode("utf-8"))
    # Get the hexadecimal representation of the hash
    sha256_hexdigest = sha256_hash.hexdigest()
    return sha256_hexdigest


print("Levenshtein")
for p in failed_tests:
    p_name = "::".join(str(p).split("::")[-2:])
    print("#" * 30)
    print(f"{p_name} with hash = {generate_sha256(str(p))}")
    for q in failed_tests:
        if p == q:
            continue
        q_name = "::".join(str(q).split("::")[-2:])
        lsr_trace, lsr_error = None, None
        similar = True
        if p.error_details and q.error_details:
            lsr_error = levenshtein_similarity_ratio(p.error_details, q.error_details)
            similar = similar and (lsr_error >= 0.95)
        if p.error_stacktrace and q.error_stacktrace:
            lsr_trace = levenshtein_similarity_ratio(
                p.error_stacktrace, q.error_stacktrace
            )
            similar = similar and (lsr_trace >= 0.95)
        if similar:
            print(
                f"..found similar test: {q_name} with error-lsr: {lsr_error} and trace-lsr: {lsr_trace}"
            )
            print(
                f"..jaccard sim: {jaccard_ngram_similarity(p.error_stacktrace, q.error_stacktrace, 5)}"
            )
            print(
                f"..cosince sim: {cosine_sim(p.error_stacktrace, q.error_stacktrace)}"
            )
            print(f"..p stacktrace:\n {p.error_stacktrace}")
            print(f"..q stacktrace:\n {q.error_stacktrace}")


import Levenshtein
