# SupaCRUD Library Development Plan

This plan outlines the development process for the SupaCRUD library, incorporating critiques and improvements based on best practices and pragmatic considerations.

## Step 1: Project Configuration & Setup

- **Critique**: The initial step is critical, as it sets the foundation of the project. The critique is that it's missing information on how to structure the `pyproject.toml` and `setup.cfg` files.

- **Improvement & Details**: You should include specific dependencies in `pyproject.toml`, such as the required Python version and necessary packages. Similarly, `setup.cfg` should contain the metadata for the package.

- **Commands**:
    ```
    touch pyproject.toml setup.cfg .gitignore
    ```

## Step 2: Project Description and Contribution Guideline

- **Critique**: The content of the `README.md` and `CONTRIBUTING.md` files isn't specified. There should be more emphasis on the quality and clarity of these documents, as they are the first things contributors see.

- **Improvement & Details**: Write comprehensive and clear instructions in both `README.md` and `CONTRIBUTING.md`. The README should include a detailed description of the project, its purpose, usage examples, and installation instructions. CONTRIBUTING should specify the project's code of conduct, how to report issues, and the process for submitting pull requests.

- **Commands**:
    ```
    touch README.md CONTRIBUTING.md
    ```

## Step 3: Version Control

- **Critique**: Initializing the Git repository after creating a few files might lead to unnecessary commits, and a clear versioning strategy isn't specified.

- **Improvement & Details**: The Git repository should be initialized at the start of the project. Use clear, concise commit messages that follow a standard format (e.g., using imperative language). A versioning strategy, like Semantic Versioning, should be adopted.

- **Commands**:
    ```
    git init
    git add .
    git commit -m "Initial commit: Basic project setup"
    ```

## Step 4: Initial Codebase

- **Critique**: There's a lack of detail on what the initial codebase should contain.

- **Improvement & Details**: The `__init__.py` file in the `supacrud/` directory should contain necessary imports that will be available when the package is imported. Initially, it might just be an empty file.

- **Commands**:
    ```
    mkdir supacrud
    touch supacrud/__init__.py
    ```

## Step 5: Database Connection and Management

- **Critique**: Not considering different types of databases that the users might want to use.

- **Improvement & Details**: Use a database abstraction layer like SQLAlchemy which can work with different types of databases. 

- **Commands**: No commands for this step, as this involves writing the Python code for database connections in the `db.py` file.

## Step 6: Core CRUD Functions/Classes

- **Critique**: The order of test writing and function implementation isn't clear in the original plan. The Test-Driven Development (TDD) approach is mentioned but isn't elaborated on.

- **Improvement & Details**: Following the TDD approach, write tests first for each function or class before implementing them. This helps ensure the code meets its requirements and behaves as expected.

- **Commands**: No specific commands for this step, as this involves writing Python code in various files in the `supacrud/` directory.

## Step 7: Base Utility/Helper Code

- **CritI apologize for the sudden interruption, here is the rest of the plan:

```markdown
ique**: There isn't a clear distinction between this step and the previous one.

- **Improvement & Details**: This step should involve the creation of shared helper functions and classes that are used across the library. The `utils.py` file typically contains functions for data conversion, validation, and other common tasks. 

- **Commands**:
    ```
    touch supacrud/utils.py
    ```

## Step 8: Tests

- **Critique**: There's a lack of detail about what the tests should cover.

- **Improvement & Details**: Tests should be comprehensive and cover edge cases. They should validate all functions and classes in the library. The test files should be created under the `tests/` directory with a clear naming convention like `test_[module_name].py`.

- **Commands**:
    ```
    mkdir tests
    touch tests/test_db.py tests/test_utils.py
    ```

## Step 9: Security and Performance

- **Critique**: This step is mentioned last, but security and performance considerations should be part of every step in the process.

- **Improvement & Details**: Instead of being a single step, this should be a continuous process throughout development. Use static code analysis tools such as `pylint` or `flake8` and performance profiling tools such as `cProfile` regularly to identify and address potential issues.

- **Commands**: No specific commands for this step, as it's more about the ongoing application of tools and best practices.

## Step 10: Documentation

- **Critique**: The role of documentation in helping users understand the API is noted, but there's no mention of documenting for developers and contributors.

- **Improvement & Details**: Documentation should also include comments and docstrings in the code, which can help contributors understand the logic and make modifications. Auto-generating API docs from these docstrings can be done using tools like Sphinx.

- **Commands**:
    ```
    mkdir docs
    touch docs/index.rst
    ```

## Step 11: Example Code

- **Critique**: Providing example code is a good idea, but there should be guidance on how to write examples that are easy to understand and demonstrate the library's capabilities effectively.

- **Improvement & Details**: The examples should be well-documented and illustrate practical use-cases of the library. Jupyter notebooks are a good choice as they allow for descriptive text between code blocks.

- **Commands**:
    ```
    mkdir examples
    touch examples/example1.py examples/example2.py
    ```

## Step 12: Packaging and Distribution

- **Critique**: Packaging and distribution were mentioned together, but the packaging process has more to it and should be broken down into more steps.

- **Improvement & Details**: Packaging involves more than just writing a `setup.py` file. It also involves creating a `MANIFEST.in` file to include non-code files in the package. Distribution can be done through various platforms like PyPi or Anaconda.

- **Commands**:
    ```
    touch setup.py MANIFEST.in
    ```

## Step 13: Continuous Integration

- **Critique**: There's no mention of continuous integration (CI) in the original plan.

- **Improvement & Details**: CI is an important part of the development process as it helps ensure the code is always in a working state. It can be done using tools like Travis CI or CircleCI.


curl -X POST 'http://192.168.1.100:54321/rest/v1/users' \
-H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "name": "John Doe", "email": "john.doe@example.com", "age": 32 }'


curl -X POST 'http://localhost:54321/rest/v1/rpc/get_story_by_email' \
-d '{ "author_email": "john.doe@example.com" }' \
-H "Content-Type: application/json" \
-H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"

