import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DATABASE_PATH = os.getenv("DATABASE_PATH", "catalog.db")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize the database when the FastAPI application starts."""
    initialize_database()
    yield


app = FastAPI(title="Catalog Service", version="1.0.0", lifespan=lifespan)


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=300)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class StockUpdate(BaseModel):
    stock: int = Field(ge=0)


class StockReservation(BaseModel):
    quantity: int = Field(gt=0)


class Product(ProductCreate):
    id: int


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with rows accessible by column name."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_session():
    """Provide a database session and commit changes after successful use."""
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def row_to_product(row: sqlite3.Row) -> Product:
    """Convert a database row into a product response model."""
    return Product(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        price=row["price"],
        stock=row["stock"],
    )


def initialize_database() -> None:
    """Create the products table if it does not already exist."""
    with db_session() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
            """)


def database_dependency():
    """Yield a database connection for FastAPI route handlers."""
    with db_session() as connection:
        yield connection


Database = Annotated[sqlite3.Connection, Depends(database_dependency)]


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health information."""
    return {"status": "ok", "service": "catalog-service"}


@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, database: Database) -> Product:
    """Create a new product in the catalog."""
    cursor = database.execute(
        """
        INSERT INTO products (name, description, price, stock)
        VALUES (?, ?, ?, ?)
        """,
        (product.name, product.description, product.price, product.stock),
    )
    product_id = cursor.lastrowid
    row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    return row_to_product(row)


@app.get("/products", response_model=list[Product])
def list_products(database: Database) -> list[Product]:
    """Return all products ordered by product ID."""
    rows = database.execute("SELECT * FROM products ORDER BY id").fetchall()
    return [row_to_product(row) for row in rows]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, database: Database) -> Product:
    """Return a single product by ID."""
    row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return row_to_product(row)


@app.patch("/products/{product_id}/stock", response_model=Product)
def update_stock(product_id: int, update: StockUpdate, database: Database) -> Product:
    """Update the available stock for an existing product."""
    row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    database.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (update.stock, product_id),
    )
    updated_row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    return row_to_product(updated_row)


@app.post("/products/{product_id}/reserve", response_model=Product)
def reserve_stock(
    product_id: int, reservation: StockReservation, database: Database
) -> Product:
    """Reserve product stock when an order is placed."""
    row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if row["stock"] < reservation.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough stock available",
        )

    new_stock = row["stock"] - reservation.quantity
    database.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (new_stock, product_id),
    )
    updated_row = database.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    return row_to_product(updated_row)
