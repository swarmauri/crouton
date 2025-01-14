# Swarmauri's CroutonClient

`CroutonClient` is a Python library for streamlined REST API interactions, supporting both **synchronous** and **asynchronous** operations for CRUD tasks.

---

### **Initialization**
```python
from crouton_client import CroutonClient

client = CroutonClient(API_ROOT="https://api.example.com", ACCESS_STRING="your-token")
```

---

### **Common Operations**

#### **GET**
- **Synchronous**:
  ```python
  response = client.get(resource="items", item_id="123", filters={"status": "active"})
  ```
- **Asynchronous**:
  ```python
  response = await client.aget(resource="items", item_id="123")
  ```

#### **POST**
- **Synchronous**:
  ```python
  response = client.post(resource="items", data_obj={"name": "Item", "price": 10.0})
  ```
- **Asynchronous**:
  ```python
  response = await client.apost(resource="items", data_obj={"name": "Item", "price": 10.0})
  ```

#### **PUT**
- **Synchronous**:
  ```python
  response = client.put(resource="items", data_obj={"price": 15.0}, item_id="123")
  ```
- **Asynchronous**:
  ```python
  response = await client.aput(resource="items", data_obj={"price": 15.0}, item_id="123")
  ```

#### **DELETE**
- **Synchronous**:
  ```python
  response = client.delete(resource="items", item_id="123")
  ```
- **Asynchronous**:
  ```python
  response = await client.adelete(resource="items", item_id="123")
  ```

---

### **Features**
1. **Synchronous & Asynchronous**: Methods available for GET, POST, PUT, DELETE.
2. **Authentication**: Pass `ACCESS_STRING` for token-based requests.
3. **Auto-Generated IDs**: `post` and `apost` auto-generate `id` fields if not provided.
4. **Logging**: Logs all requests and responses for debugging.

---

### **Error Handling**
Raises `ValueError` for failed requests:
```python
try:
    client.get(resource="invalid")
except ValueError as e:
    print(f"Error: {e}")
```

---

### **Summary Table**

| Operation | Synchronous         | Asynchronous       |
|-----------|----------------------|--------------------|
| **GET**   | `get()`              | `aget()`           |
| **POST**  | `post()`             | `apost()`          |
| **PUT**   | `put()`              | `aput()`           |
| **DELETE**| `delete()`           | `adelete()`        |

`CroutonClient` simplifies REST API interactions, allowing you to focus on application logic instead of repetitive request handling.
