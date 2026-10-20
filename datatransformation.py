import boto3
import pandas as pd
from io import BytesIO

# S3 configuration
bucket_name = "harshdatatest"
region = "us-east-1"

# Connect to S3
s3 = boto3.client("s3", region_name=region)

# 1. Read cleaned data from S3
response = s3.get_object(
    Bucket=bucket_name,
    Key="newdata.csv"
)

df = pd.read_csv(BytesIO(response["Body"].read()))

print("Original data:")
print(df.head())

# 2. Rename columns
df = df.rename(columns={
    "student_name": "name",
    "attendance_percent": "attendance"
})

# 3. Convert data types
for col in ["age", "marks", "attendance", "fee_paid"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 4. Create a grade column based on marks
if "marks" in df.columns:
    df["grade"] = pd.cut(
        df["marks"],
        bins=[-float("inf"), 39, 59, 74, 89, 100],
        labels=["F", "D", "C", "B", "A"]
    )

# 5. Create an attendance status
if "attendance" in df.columns:
    df["attendance_status"] = df["attendance"].apply(
        lambda x: (
            "Low" if pd.notna(x) and x < 75
            else "Good" if pd.notna(x)
            else "Unknown"
        )
    )

# 6. Create a fee status
if "fee_paid" in df.columns:
    df["fee_status"] = df["fee_paid"].apply(
        lambda x: (
            "Pending" if pd.isna(x) or x == 0
            else "Paid"
        )
    )

# 7. Filter students with marks >= 80
if "marks" in df.columns:
    high_scorers = df[df["marks"] >= 80]
    print("\nHigh-scoring students:")
    print(high_scorers.head())

# 8. Sort by marks, highest first
if "marks" in df.columns:
    df = df.sort_values(
        by="marks",
        ascending=False,
        na_position="last"
    )

# 9. Save transformed data locally
output_file = "transformed_data.csv"
df.to_csv(output_file, index=False)

# 10. Upload transformed data to S3
s3.upload_file(
    output_file,
    bucket_name,
    "transformed_data.csv"
)

print("\nTransformation completed successfully!")
print("Local file:", output_file)
print("S3 file: s3://harshdatatest/transformed_data.csv")