from flask import Flask
from models import db, Car
from config import Config
import time

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def measure_query_time(query_func, *args, **kwargs):
    """Вимірювання часу виконання запиту."""
    start_time = time.time()
    query_func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time

def insert_test(n):
    """Тест вставки записів."""
    cars = [Car(make=f"Make {i}", model=f"Model {i}", year=2000 + i % 20, price=20000 + i % 5000) for i in range(n)]
    db.session.bulk_save_objects(cars)
    db.session.commit()

def select_test():
    """Тест вибірки всіх записів."""
    return Car.query.all()

def update_test():
    """Тест оновлення одного запису."""
    car = Car.query.first()
    if car:
        car.price += 1000
        db.session.commit()

def delete_test():
    """Тест видалення одного запису."""
    car = Car.query.first()
    if car:
        db.session.delete(car)
        db.session.commit()

def benchmark_operations():
    """Заміри операцій."""
    results = {}
    for n in [1000, 10000, 100000, 1000000]:
        print(f"Testing with {n} records...")

        # Drop and recreate tables
        db.drop_all()
        db.create_all()

        # Insert
        insert_time = measure_query_time(insert_test, n)
        results[f"Insert {n}"] = insert_time

        # Select
        select_time = measure_query_time(select_test)
        results[f"Select {n}"] = select_time

        # Update
        update_time = measure_query_time(update_test)
        results[f"Update {n}"] = update_time

        # Delete
        delete_time = measure_query_time(delete_test)
        results[f"Delete {n}"] = delete_time

    return results

def print_results(results):
    """Вивід результатів у таблиці."""
    print("\nBenchmark Results:")
    print("{:<12} {:<10}".format("Operation", "Time (s)"))
    print("-" * 25)
    for operation, time_taken in results.items():
        print(f"{operation:<12} {time_taken:.5f}")

if __name__ == "__main__":
    with app.app_context():
        print("Starting benchmark tests...")
        benchmark_results = benchmark_operations()
        print_results(benchmark_results)
