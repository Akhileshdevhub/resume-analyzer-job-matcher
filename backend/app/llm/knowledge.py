"""Deterministic knowledge base for the template (no-LLM) path.

This is what powers recommendations and interview questions when no LLM is
configured. It's a curated, honest mapping — concrete project ideas and real
interview questions per skill — so the fallback is genuinely useful, not filler.
Anything not listed gets a sensible generic template.
"""
from __future__ import annotations

# skill -> a concrete, resume-worthy project idea that teaches it.
PROJECT_IDEAS: dict[str, str] = {
    "Docker": "Containerise one of your existing apps with a Dockerfile and docker-compose, and document how to run it in one command.",
    "Kubernetes": "Deploy a small multi-service app to a local Kubernetes cluster (minikube/kind) with Deployments and Services.",
    "AWS": "Deploy a small API to AWS (EC2 or Elastic Beanstalk) and write up the setup, cost, and teardown steps.",
    "Google Cloud Platform": "Deploy a containerised service to Google Cloud Run and wire up a managed database.",
    "Azure": "Host a web API on Azure App Service and connect it to Azure Database for PostgreSQL.",
    "TensorFlow": "Rebuild one of your PyTorch models in TensorFlow/Keras and compare training code and results.",
    "PyTorch": "Train a small neural network in PyTorch (e.g. image or text classification) and log metrics per epoch.",
    "MLOps": "Add experiment tracking (MLflow) and a simple CI check to an existing ML project so runs are reproducible.",
    "PostgreSQL": "Design a normalised PostgreSQL schema for a real dataset and write the analytical queries it enables.",
    "Redis": "Add a Redis cache in front of an expensive endpoint and measure the latency improvement.",
    "Apache Kafka": "Build a small producer/consumer pipeline with Kafka that processes a stream of events.",
    "GraphQL": "Expose an existing REST resource through a GraphQL API and compare the two query styles.",
    "React": "Build a small React front-end that consumes one of your existing APIs.",
    "Spring Boot": "Build a REST API in Spring Boot backed by a relational database with a few endpoints and tests.",
    "Natural Language Processing": "Build a text-classification project (e.g. topic or sentiment) end to end, from cleaning to evaluation.",
    "Machine Learning": "Take a tabular dataset from problem framing to a validated model, and write up your methodology.",
}

# skill -> a couple of real interview questions that skill invites.
INTERVIEW_QUESTIONS: dict[str, list[str]] = {
    "Python": ["What's the difference between a list and a tuple, and when would you use each?",
               "How does Python manage memory and what is the GIL?"],
    "SQL": ["What's the difference between an INNER JOIN and a LEFT JOIN?",
            "How would you find and fix a slow query?"],
    "Machine Learning": ["How do you tell whether your model is overfitting?",
                         "Explain the bias-variance trade-off."],
    "Deep Learning": ["Why do we need activation functions in a neural network?",
                      "What is backpropagation, at a high level?"],
    "PyTorch": ["What does autograd do in PyTorch?",
                "Walk me through a typical training loop."],
    "REST APIs": ["What makes an API RESTful?",
                  "How do you design pagination for a list endpoint?"],
    "Docker": ["What's the difference between an image and a container?",
               "Why are Docker layers useful and how does caching work?"],
    "AWS": ["What compute options would you consider to host a small API, and how would you choose?",
            "How would you keep secrets out of your deployed application?"],
    "PostgreSQL": ["When would you add an index, and what's the downside of too many?",
                   "What does a transaction give you (ACID)?"],
    "Kubernetes": ["What problem does Kubernetes solve that plain Docker doesn't?",
                   "What is a Pod versus a Deployment?"],
    "Data Structures": ["When would you use a hash map over a sorted array?",
                        "How would you detect a cycle in a linked list?"],
}

# skill -> a short "what to learn" pointer.
LEARNING_TOPICS: dict[str, str] = {
    "Docker": "Images vs containers, Dockerfiles, layer caching, docker-compose.",
    "AWS": "Core services (EC2, S3, IAM), the shared-responsibility model, and how to deploy a small app.",
    "MLOps": "Experiment tracking, model versioning, reproducible pipelines, and monitoring.",
    "TensorFlow": "The Keras API, tensors, and how training differs from PyTorch.",
    "Kubernetes": "Pods, Deployments, Services, and why orchestration matters at scale.",
    "PostgreSQL": "Indexing, query planning (EXPLAIN), transactions, and normalisation.",
}


def project_idea(skill: str) -> str:
    return PROJECT_IDEAS.get(
        skill, f"Build a small, focused project that uses {skill} so you can speak to it concretely."
    )


def interview_questions_for(skill: str) -> list[str]:
    return INTERVIEW_QUESTIONS.get(
        skill, [f"Can you explain the fundamentals of {skill} and where you'd apply it?"]
    )


def learning_topic(skill: str) -> str:
    return LEARNING_TOPICS.get(skill, f"Core concepts of {skill} and one hands-on exercise.")
