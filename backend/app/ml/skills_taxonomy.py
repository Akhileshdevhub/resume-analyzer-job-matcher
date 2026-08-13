"""Curated skill taxonomy.

This is the heart of skill *normalisation*: a hand-maintained dictionary that
maps every surface form of a skill ("Postgres", "postgresql", "psql") to one
canonical name ("PostgreSQL") and a category (language / framework / …).

Why a curated taxonomy instead of "let the model figure it out"?
  * It is fully explainable — we can always say why "JS" became "JavaScript".
  * It is accurate for a known universe of skills, with zero training data.
  * It is honest about its limits: a skill not in the taxonomy simply is not
    recognised, which is a documented limitation rather than a silent guess.

Trade-off: it needs maintenance and won't catch brand-new or niche skills. For a
resume/JD matcher over mainstream tech skills, that trade is worth it.

All alias strings are stored lowercased because matching runs on a lowercased,
punctuation-light form of the text (see `text_cleaning.normalise_for_matching`).
"""
from __future__ import annotations

from dataclasses import dataclass

# Category labels (kept as plain strings for easy JSON serialisation).
LANGUAGE = "language"
FRAMEWORK = "framework"
LIBRARY = "library"
ML = "ml"
CLOUD = "cloud"
DATABASE = "database"
TOOL = "tool"
CONCEPT = "concept"

CATEGORY_LABELS = {
    LANGUAGE: "Programming Languages",
    FRAMEWORK: "Frameworks",
    LIBRARY: "Libraries",
    ML: "ML / Data Science",
    CLOUD: "Cloud Platforms",
    DATABASE: "Databases",
    TOOL: "Tools & DevOps",
    CONCEPT: "Concepts",
}


@dataclass(frozen=True)
class Skill:
    canonical: str
    category: str
    aliases: tuple[str, ...]


# Every entry: canonical name, category, and the surface forms that map to it.
# The canonical name (lowercased) is always an implicit alias — no need to
# repeat it in the aliases tuple.
_SKILLS: list[Skill] = [
    # ---- Languages ----
    Skill("Python", LANGUAGE, ("py",)),
    Skill("C++", LANGUAGE, ("cpp", "cplusplus")),
    Skill("C", LANGUAGE, ("c programming", "c language")),
    Skill("Java", LANGUAGE, ()),
    Skill("JavaScript", LANGUAGE, ("js", "ecmascript")),
    Skill("TypeScript", LANGUAGE, ("ts",)),
    Skill("SQL", LANGUAGE, ()),
    Skill("Go", LANGUAGE, ("golang",)),
    Skill("C#", LANGUAGE, ("csharp", "c sharp")),
    Skill("Ruby", LANGUAGE, ()),
    Skill("PHP", LANGUAGE, ()),
    Skill("Scala", LANGUAGE, ()),
    Skill("Kotlin", LANGUAGE, ()),
    Skill("Swift", LANGUAGE, ()),
    Skill("Rust", LANGUAGE, ()),
    Skill("MATLAB", LANGUAGE, ("matlab",)),
    Skill("R", LANGUAGE, ("r language", "r programming")),
    Skill("Bash", LANGUAGE, ("shell scripting", "shell")),
    # ---- Frameworks ----
    Skill("FastAPI", FRAMEWORK, ("fast api",)),
    Skill("Flask", FRAMEWORK, ()),
    Skill("Django", FRAMEWORK, ()),
    Skill("Spring Boot", FRAMEWORK, ("spring", "springboot")),
    Skill("React", FRAMEWORK, ("react.js", "reactjs")),
    Skill("Angular", FRAMEWORK, ("angular.js", "angularjs")),
    Skill("Vue", FRAMEWORK, ("vue.js", "vuejs")),
    Skill("Node.js", FRAMEWORK, ("node", "nodejs")),
    Skill("Express", FRAMEWORK, ("express.js", "expressjs")),
    Skill("Next.js", FRAMEWORK, ("nextjs", "next")),
    Skill(".NET", FRAMEWORK, ("dotnet", "asp.net")),
    Skill("Ruby on Rails", FRAMEWORK, ("rails", "ror")),
    Skill("Tailwind CSS", FRAMEWORK, ("tailwind", "tailwindcss")),
    # ---- Libraries (ML / data) ----
    Skill("scikit-learn", LIBRARY, ("sklearn", "scikit learn")),
    Skill("PyTorch", LIBRARY, ("pytorch", "torch")),
    Skill("TensorFlow", LIBRARY, ("tensorflow",)),
    Skill("Keras", LIBRARY, ()),
    Skill("pandas", LIBRARY, ()),
    Skill("NumPy", LIBRARY, ("numpy",)),
    Skill("SciPy", LIBRARY, ("scipy",)),
    Skill("Hugging Face Transformers", LIBRARY, ("transformers", "hugging face", "huggingface")),
    Skill("OpenCV", LIBRARY, ("opencv", "open cv")),
    Skill("XGBoost", LIBRARY, ("xgboost",)),
    Skill("LightGBM", LIBRARY, ("lightgbm",)),
    Skill("spaCy", LIBRARY, ("spacy",)),
    Skill("NLTK", LIBRARY, ()),
    Skill("Matplotlib", LIBRARY, ("matplotlib",)),
    # ---- ML / Data Science concepts ----
    Skill("Machine Learning", ML, ("ml",)),
    Skill("Deep Learning", ML, ("dl",)),
    Skill("Natural Language Processing", ML, ("nlp",)),
    Skill("Computer Vision", ML, ()),  # "cv" alias omitted: collides with "curriculum vitae"
    Skill("Neural Networks", ML, ("neural network",)),  # "ann" omitted: collides with the name "Ann"
    Skill("Convolutional Neural Networks", ML, ("cnn", "convolutional neural network")),
    Skill("Recurrent Neural Networks", ML, ("rnn", "lstm")),
    Skill("Reinforcement Learning", ML, ("rl",)),
    Skill("Data Science", ML, ()),
    Skill("Data Analysis", ML, ("data analytics",)),
    Skill("Feature Engineering", ML, ()),
    Skill("Model Deployment", ML, ("model serving",)),
    Skill("MLOps", ML, ("ml ops",)),
    Skill("Large Language Models", ML, ("llm", "llms")),
    # ---- Cloud ----
    Skill("AWS", CLOUD, ("amazon web services",)),
    Skill("Google Cloud Platform", CLOUD, ("gcp", "google cloud")),
    Skill("Azure", CLOUD, ("microsoft azure",)),
    Skill("Heroku", CLOUD, ()),
    Skill("Vercel", CLOUD, ()),
    # ---- Databases ----
    Skill("PostgreSQL", DATABASE, ("postgres", "psql", "postgresql")),
    Skill("MySQL", DATABASE, ("my sql",)),
    Skill("SQLite", DATABASE, ("sqlite3",)),
    Skill("MongoDB", DATABASE, ("mongo",)),
    Skill("Redis", DATABASE, ()),
    Skill("Elasticsearch", DATABASE, ("elastic search",)),
    Skill("Cassandra", DATABASE, ()),
    Skill("DynamoDB", DATABASE, ("dynamo",)),
    Skill("Oracle", DATABASE, ("oracle db",)),
    # ---- Tools / DevOps ----
    Skill("Docker", TOOL, ()),
    Skill("Kubernetes", TOOL, ("k8s",)),
    Skill("Git", TOOL, ()),
    Skill("GitHub", TOOL, ("git hub",)),
    Skill("GitLab", TOOL, ("git lab",)),
    Skill("Jenkins", TOOL, ()),
    Skill("CI/CD", TOOL, ("ci cd", "continuous integration", "continuous deployment")),
    Skill("Linux", TOOL, ("unix",)),
    Skill("Terraform", TOOL, ()),
    Skill("Apache Airflow", TOOL, ("airflow",)),
    Skill("Apache Kafka", TOOL, ("kafka",)),
    Skill("RabbitMQ", TOOL, ("rabbit mq",)),
    Skill("Apache Spark", TOOL, ("spark", "pyspark")),
    Skill("Hadoop", TOOL, ()),
    Skill("Jupyter", TOOL, ("jupyter notebook",)),
    # ---- Concepts ----
    Skill("REST APIs", CONCEPT, ("rest", "rest api", "restful", "restful api", "restful apis")),
    Skill("GraphQL", CONCEPT, ("graph ql",)),
    Skill("Microservices", CONCEPT, ("micro services",)),
    Skill("Object-Oriented Programming", CONCEPT, ("oop", "object oriented programming")),
    Skill("Data Structures", CONCEPT, ("dsa",)),
    Skill("Algorithms", CONCEPT, ()),
    Skill("Agile", CONCEPT, ("scrum",)),
    Skill("Unit Testing", CONCEPT, ("unit tests", "pytest", "junit")),
    Skill("System Design", CONCEPT, ()),
]

# Short, ambiguous aliases that appear as ordinary English words too. For these
# we require a "list-like" context (a delimiter such as a comma, slash, pipe, or
# line boundary on at least one side) before counting a match, to keep precision
# high. See skill_extractor._is_list_context.
# Only aliases that are ALSO ordinary English words need the list-context guard.
# Abbreviations like "ml", "js", "ts", "dl" aren't English words, so the boundary
# look-arounds alone keep them safe (e.g. "ml" can't match inside "html").
AMBIGUOUS_ALIASES: frozenset[str] = frozenset({"c", "go", "r"})


# ---------------------------------------------------------------------------
# Related-skill ontology.
#
# Each group lists canonical skills that are close substitutes or siblings. It
# powers "related" matches deterministically: if a JD wants TensorFlow and the
# resume has PyTorch, they share the "deep-learning frameworks" group, so we can
# say *why* they're related ("both are deep-learning frameworks") instead of just
# printing a cosine number. This works with zero ML dependencies and complements
# the embedding-based semantic match when that backend is available.
# ---------------------------------------------------------------------------
_RELATED_GROUPS: list[set[str]] = [
    {"PyTorch", "TensorFlow", "Keras"},                       # deep-learning frameworks
    {"Machine Learning", "Deep Learning", "Neural Networks",
     "Convolutional Neural Networks", "Recurrent Neural Networks"},
    {"scikit-learn", "XGBoost", "LightGBM"},                  # classical ML libraries
    {"Natural Language Processing", "spaCy", "NLTK",
     "Hugging Face Transformers", "Large Language Models"},
    {"AWS", "Google Cloud Platform", "Azure"},                # cloud providers
    {"PostgreSQL", "MySQL", "SQLite", "Oracle", "SQL"},       # relational databases
    {"MongoDB", "Redis", "Cassandra", "DynamoDB"},            # NoSQL / key-value stores
    {"React", "Angular", "Vue", "Next.js"},                   # frontend frameworks
    {"Flask", "FastAPI", "Django"},                           # python web frameworks
    {"Spring Boot", "Ruby on Rails", ".NET", "Express"},      # backend web frameworks
    {"Docker", "Kubernetes"},                                 # containers / orchestration
    {"Git", "GitHub", "GitLab"},                              # version control
    {"Jenkins", "CI/CD", "Terraform"},                        # devops / automation
    {"Apache Kafka", "RabbitMQ"},                             # message queues
    {"Apache Spark", "Hadoop", "Apache Airflow"},             # big-data / pipelines
    {"pandas", "NumPy", "SciPy", "Matplotlib"},               # python data stack
    {"REST APIs", "GraphQL", "Microservices"},                # API styles
    {"Java", "Kotlin", "Scala"},                              # JVM languages
    {"JavaScript", "TypeScript"},                             # JS family
    {"C", "C++", "Rust", "Go"},                               # systems languages
]


def _build_related_map() -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for group in _RELATED_GROUPS:
        for skill in group:
            mapping.setdefault(skill, set()).update(group - {skill})
    return mapping


RELATED_MAP: dict[str, set[str]] = _build_related_map()


def related_canonicals(canonical: str) -> set[str]:
    """Return the set of skills curated as related to `canonical` (may be empty)."""
    return RELATED_MAP.get(canonical, set())


def _build_lookup() -> tuple[dict[str, Skill], dict[str, str]]:
    """Build alias->Skill and canonical->category maps once at import time.

    Longer aliases are registered first so that, when we scan, multi-word skills
    ("machine learning") win over any substring collisions.
    """
    alias_to_skill: dict[str, Skill] = {}
    canonical_to_category: dict[str, str] = {}
    for skill in _SKILLS:
        canonical_to_category[skill.canonical] = skill.category
        forms = {skill.canonical.lower(), *skill.aliases}
        for form in forms:
            # Don't let a shorter alias overwrite a more specific earlier one.
            alias_to_skill.setdefault(form, skill)
    return alias_to_skill, canonical_to_category


ALIAS_TO_SKILL, CANONICAL_TO_CATEGORY = _build_lookup()

# All alias forms, longest first — scanning in this order means we try to match
# "machine learning" before "ml", "spring boot" before "spring", etc.
ALL_ALIASES_LONGEST_FIRST: list[str] = sorted(ALIAS_TO_SKILL.keys(), key=len, reverse=True)


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category.title())
