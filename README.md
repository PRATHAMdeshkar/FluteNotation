# HandRec – Hand Gesture to Flute Note Recognition

This project demonstrates a **structural pipeline** for detecting hand gestures (flute finger positions), mapping them to **musical notations (Sa, Re, Ga, Ma...)**, and storing the detected notes into a **PostgreSQL database** through **Kafka streaming**.

---

## 📌 Architecture Flow

**Camera → Mediapipe (ML Model) → Producer → Kafka → Consumer → PostgreSQL (Data Lake)**

- **Video Cam**: Captures live hand gestures.  
- **Mediapipe (ML Model)**: Detects finger up/down positions and converts them into flute notes.  
- **Producer**: Sends notes into Kafka topic.  
- **Kafka + Zookeeper**: Message broker layer.  
- **Consumer**: Listens to Kafka topic and stores the notes into PostgreSQL.  
- **PostgreSQL**: Acts as a storage/data lake for all detected notations.  

---

## 🛠️ Prerequisites

- **Docker & Docker Compose** (for Kafka, Zookeeper, PostgreSQL)  
- **Python 3.8+**  
- Webcam  

---

## ⚙️ Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/PRATHAMdeshkar/FluteNotation
cd HandRec
```
Install Python Dependencies
```
pip install -r requirements.txt
```

### 2. Start Infrastructure (Kafka, Zookeeper, PostgreSQL)
```bash
$ docker compose -f docker-compose.yml up -d
$ docker ps
```
## Running the Project
### Step 1: Run Consumer (listen & save notes to DB)
```bash
python consumer.py
```
<img width="1135" height="175" alt="Screenshot from 2025-09-06 11-14-38" src="https://github.com/user-attachments/assets/f221b617-7455-430c-8084-eaeb30ada702" />


### Step 2: Run Producer (hand gesture recognition)

```bash
python handGesture.py
```
<img width="1918" height="1009" alt="Screenshot from 2025-09-06 11-16-53" src="https://github.com/user-attachments/assets/7139271b-3f27-419b-9b42-a8960832dba2" />


Opens webcam.
Detects hand gestures → maps to notes → pushes to Kafka.

### Step 3: Verify Data in PostgreSQL
```bash
Enter Postgres container:
$ docker exec -it 845d54e95831 psql -U postgres -d flute
>>Inside DB>># SELECT * FROM notes;
```
<img width="576" height="953" alt="Screenshot from 2025-09-06 11-13-21" src="https://github.com/user-attachments/assets/6d3bde78-3e3d-4556-bddb-7f129068745a" />


---
# Flow Recap
### Camera → Mediapipe → Producer → Kafka → Consumer → Postgres
