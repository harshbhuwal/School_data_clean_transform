import boto3
import pandas as pd
from io import BytesIO

# S3 configuration
bucket_name = "harshdatatest"
region = "us-east-1"
file_key = "DYCD_after-school_programs__Neighborhood_Development_Area__NDA__Family_Support.csv"

# Connect to S3
s3 = boto3.client("s3", region_name=region)

# Read the original CSV from S3
response = s3.get_object(
    Bucket=bucket_name,
    Key=file_key
)

df = pd.read_csv(BytesIO(response["Body"].read()))

print("Original data:")
print(df.head())

# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Standardize text columns
for col in ["student_name", "city"]:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip().str.title()

# Standardize gender
if "gender" in df.columns:
    df["gender"] = (
        df["gender"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace({"m": "male", "f": "female"})
    )

# Convert numeric columns
for col in ["age", "attendance_percent", "marks", "fee_paid"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Apply validation rules
if "age" in df.columns:
    df.loc[~df["age"].between(0, 120), "age"] = pd.NA

if "attendance_percent" in df.columns:
    df.loc[~df["attendance_percent"].between(0, 100),
           "attendance_percent"] = pd.NA

if "marks" in df.columns:
    df.loc[~df["marks"].between(0, 100), "marks"] = pd.NA

if "fee_paid" in df.columns:
    df.loc[df["fee_paid"] < 0, "fee_paid"] = pd.NA

# Standardize common missing-value placeholders
df = df.replace(
    r"(?i)^\s*(unknown|n/a|none|-)\s*$",
    pd.NA,
    regex=True
)

# Remove exact duplicate rows
df = df.drop_duplicates()

# Save locally with the new name
output_file = "newdata.csv"
df.to_csv(output_file, index=False)

print(f"Cleaned file saved locally as {output_file}")

# Upload the cleaned file to S3 with the new name
s3.upload_file(
    output_file,
    bucket_name,
    "newdata.csv"
)

print("Uploaded successfully to S3 as newdata.csv")