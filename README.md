# european-bank-churn-analysis
Customer Churn Analysis Dashboard - ECB Commissioned Study

## Dashboard Link
http://localhost:8505/

## Resarch Paper Link
https://zenodo.org/records/19565671

---

# 🏦 ECB Customer Churn Analytics Dashboard

> A production-grade interactive analytics dashboard built for European retail banking — designed to uncover, visualize, and act on customer churn patterns using real-world data.

---

## 🚀 Overview

This project is a **full-stack data analytics application** built with **Streamlit + Plotly**, enabling stakeholders to:

* Identify **high-risk churn segments**
* Analyze **customer behavior patterns**
* Quantify **revenue at risk**
* Generate **executive-level insights**

It transforms raw banking data into a **decision-making tool**, not just a dashboard.

---

## 🎯 Key Highlights

* 📊 9 fully interactive analytics modules
* ⚡ Real-time filtering across all visualizations
* 📉 Churn risk segmentation & KPI tracking
* 🌍 Geographic and demographic breakdowns
* 💰 Revenue impact & high-value customer analysis
* 📋 Executive-ready summary with recommendations

---

## 🧠 Business Objective

To help banking stakeholders answer:

* **Who is churning?**
* **Why are they leaving?**
* **Which customers are most valuable yet at risk?**
* **What actions should be taken?**

---

## 🖥️ Dashboard Modules

| Module                   | Description                                     |
| ------------------------ | ----------------------------------------------- |
| 📊 Overview              | Key KPIs, churn rate, segment distribution      |
| 🚦 PM Dashboard          | Risk signals, prioritization, revenue waterfall |
| 🔍 Data Validation & EDA | Data quality checks + statistical exploration   |
| 🌍 Geographic Analysis   | Country-wise churn trends and comparisons       |
| 👥 Demographics          | Age, gender, tenure-based churn patterns        |
| 💰 Financial Profile     | Balance distribution and revenue insights       |
| 💵 Salary Analysis       | Salary bands vs churn behavior                  |
| ⭐ High-Value Customers   | Top revenue contributors at risk                |
| 📋 Executive Summary     | Strategic insights & recommendations            |

---

## 🗂️ Project Structure

```
├── app.py                      # Main Streamlit application
├── European_Bank__1_.csv       # Dataset (10,000 customers)
├── README.md                   # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/ecb-churn-analytics.git
cd ecb-churn-analytics
```

### 2️⃣ Install Dependencies

```bash
pip install streamlit pandas numpy plotly
```

### 3️⃣ Add Dataset

Ensure the dataset is placed in the root directory:

```
European_Bank__1_.csv
```

### 4️⃣ Run Application

```bash
python -m streamlit run app.py
```

### 5️⃣ Open in Browser

```
http://localhost:8501
```

---

## 📊 Dataset Description

| Feature         | Description             |
| --------------- | ----------------------- |
| CustomerId      | Unique ID               |
| CreditScore     | Creditworthiness score  |
| Geography       | France, Germany, Spain  |
| Gender          | Male / Female           |
| Age             | Customer age            |
| Tenure          | Years with bank         |
| Balance         | Account balance         |
| NumOfProducts   | Products owned          |
| HasCrCard       | Credit card status      |
| IsActiveMember  | Activity status         |
| EstimatedSalary | Annual income           |
| Exited          | Churn (Target Variable) |

---

## ✅ Data Validation Engine

The app performs automated checks:

* ✔ No missing values
* ✔ Unique customer IDs
* ✔ Valid binary fields
* ✔ Realistic churn range (5–50%)
* ✔ Valid country categories
* ✔ Age & credit score validation

---

## 🎛️ Interactive Filters

All modules respond dynamically to sidebar filters:

* 🌍 Geography
* 👤 Gender
* 🎂 Age Groups
* 💳 Credit Score Bands
* 🟢 Activity Status
* 💼 Credit Card Ownership

---

## 📈 Key Insights

* 📊 **Age is the strongest churn driver**
* 🌍 **Germany shows highest churn rate**
* ⚠️ **Inactive users churn ~2× more**
* 💡 **3–4 product users show unexpected high churn**
* 💰 **High-value customers are also at risk**

---

## 🛠️ Tech Stack

| Tool      | Role                       |
| --------- | -------------------------- |
| Streamlit | Frontend + App Framework   |
| Pandas    | Data Processing            |
| NumPy     | Numerical Computing        |
| Plotly    | Interactive Visualizations |

---

## 💼 Use Cases

* Banking analytics teams
* Product managers
* Risk & retention teams
* Business strategy & leadership

---

## 📄 License

This project is developed for analytical and educational purposes using anonymized data.

---

## 🤝 Connect With Me

* 💼 LinkedIn: [https://www.linkedin.com/in/ram-prakash-patel-62863b378/](https://www.linkedin.com/in/ram-prakash-patel-62863b378/)
* 💻 GitHub: [https://github.com/Ramprakas87](https://github.com/Ramprakas87)
* 📧 Email: [ram8756patel@gmail.com](mailto:ram8756patel@gmail.com)

---

