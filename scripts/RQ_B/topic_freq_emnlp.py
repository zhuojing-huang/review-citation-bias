import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


def compute_topic_distribution(file_path):
    df = pd.read_csv(file_path)
    topic_freq = defaultdict(int)
    total_freq = 0

    for _, row in df.iterrows():
        freq = int(row['frequency'])
        topics = [str(row['topic 1']).strip(), str(row['topic 2']).strip()]

        # Skip if either topic is "Other/Unknown"
        if any(topic == "Other/Unknown" for topic in topics):
            continue

        for topic in topics:
            if topic and topic.lower() != 'nan':
                topic_freq[topic] += freq
                total_freq += freq

    topic_distribution = {
        topic: freq / total_freq for topic, freq in topic_freq.items()
    }

    return topic_distribution



def plot_top_topics(distribution, title):
    sorted_topics = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    topics, values = zip(*sorted_topics)

    plt.figure(figsize=(10, 5))
    plt.barh(topics[::-1], values[::-1], color='skyblue')
    plt.xlabel("Frequency")
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_comparison(dist1, dist2, title, top_n=20):
    # Merge topics
    all_topics = set(dist1) | set(dist2)
    combined = {
        topic: (dist1.get(topic, 0), dist2.get(topic, 0))
        for topic in all_topics
    }

    # Get top N by max frequency
    top_topics = sorted(combined.items(), key=lambda x: max(x[1]), reverse=True)[:top_n]
    topics = [t[0] for t in top_topics]

    # Convert to percentages
    values1 = [dist1.get(t, 0) * 100 for t in topics]
    values2 = [dist2.get(t, 0) * 100 for t in topics]

    x = np.arange(len(topics))
    width = 0.35

    plt.figure(figsize=(12, 6))
    bars1 = plt.bar(x - width/2, values1, width, label='Submitted Papers', color='steelblue')
    bars2 = plt.bar(x + width/2, values2, width, label='Recommended Papers', color='orange')

    max_height = max(values1 + values2)
    plt.ylim(0, max_height * 1.15)

    # Add percentage labels (smaller font size)
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=7)
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=7)

    plt.xticks(x, topics, rotation=45, ha='right')
    plt.ylabel('Percentage (%)')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_difference(dist1, dist2, title, top_n=20):
    all_topics = set(dist1) | set(dist2)
    diffs = {
        topic: dist1.get(topic, 0) - dist2.get(topic, 0)
        for topic in all_topics
    }

    top_diffs = sorted(diffs.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    topics, differences = zip(*top_diffs)

    colors = ['green' if diff > 0 else 'red' for diff in differences]

    plt.figure(figsize=(12, 6))
    plt.barh(topics[::-1], differences[::-1], color=colors[::-1])
    plt.axvline(0, color='black', linewidth=0.8)
    plt.xlabel('Difference (Submitted Papers for EMNLP2023 - Recommended Papers for EMNLP2023)')
    plt.title(title)
    plt.tight_layout()
    plt.show()


file1 = 'EMNLP_submitted_topics_annotated.csv'
file2 = 'EMNLP_recommended_topics_annotated.csv'

dist1 = compute_topic_distribution(file1)
dist2 = compute_topic_distribution(file2)

print("Distribution for Submitted Papers for EMNLP2023:")
for topic, val in dist1.items():
    print(f"{topic}: {val:.4f}")

print("\nDistribution for Recommended Papers for EMNLP2023:")
for topic, val in dist2.items():
    print(f"{topic}: {val:.4f}")


#plot_top_topics(dist1, "Top 10 Topics - Submitted Papers for EMNLP2023")
#plot_top_topics(dist2, "Top 10 Topics - Recommended Papers for EMNLP2023")


plot_comparison(dist1, dist2, "Topic Comparison for Submitted and Recommended Papers in EMNLP2023")
#plot_difference(dist1, dist2, "Diverging Difference in Topic Distribution (Top 10)")