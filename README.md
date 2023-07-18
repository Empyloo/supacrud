<<<<<<< HEAD
# supacrud
SupaCRUD is a Python library that provides a comprehensive interface to interact with Supabase, a full-stack Backend-as-a-Service platform.
=======
# SupaCRUD

SupaCRUD is a Python library that provides a comprehensive interface to interact with Supabase, a full-stack Backend-as-a-Service platform. With SupaCRUD, you can seamlessly perform Create, Read, Update, and Delete (CRUD) operations on your Supabase tables. In addition, SupaCRUD provides a robust interface to invoke remote procedure calls (RPCs) on your database.

## Structure

The project follows a structured layout with isolated modules for each database operation to enhance maintainability and readability. Here's a brief overview of the main directories and files:

- `supacrud/`: Core package containing the implementation of CRUD operations and RPC invocations.
- `tests/`: Contains unit tests to verify the functionality of the SupaCRUD package.
- `docs/`: In-depth documentation about using the SupaCRUD package.
- `setup.cfg`: Configuration file for setuptools.
- `pyproject.toml`: Specifies build system requirements and constraints.
- `README.md`: This file, providing an overview of the project.

## Setup

To get started with SupaCRUD, clone the repository and navigate into the cloned directory:

```bash
git clone https://github.com/yourusername/supacrud.git
cd supacrud
```

Next, we recommend creating a virtual environment and installing the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Using SupaCRUD is straightforward. Here's a quick example demonstrating a CREATE operation on a Supabase table:

```python
from supacrud import Supabase

# Initialize a Supabase client
client = Supabase("your_supabase_url", "your_supabase_key")

# Perform a CREATE operation
client.create("your_table", {"column1": "value1", "column2": "value2"})
```

## Contributing

We welcome contributions to SupaCRUD! If you're interested in contributing, please take a look at our contribution guidelines.

## License



>>>>>>> 6e0b42a (Initial commit: Basic project setup)
