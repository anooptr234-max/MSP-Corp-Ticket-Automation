import pandas as pd


def clean_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """Loads and sanitizes the IT service tickets dataset."""
    print("-> Reading CSV file...")
    df = pd.read_csv(csv_path)

    # Drop rows missing crucial text fields
    df = df.dropna(subset=['Document', 'Topic_group'])

    # Strip whitespace and create a composite field for optimal semantic matching
    df['Document'] = df['Document'].str.strip()
    df['Topic_group'] = df['Topic_group'].str.strip()
    df['page_content'] = "Historical Category: " + df['Topic_group'] + " | Ticket Context: " + df['Document']

    return df