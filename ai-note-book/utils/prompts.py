from typing import Dict

KNOWLEDGE_GRAPH_EXTRACTION_PROMPT = """
# Role: Knowledge Graph Construction Assistant
You are an assistant skilled at extracting structured data from text, capable of identifying entities, relationships, and attributes, and organizing them into the format required for a knowledge graph.

##Core Tasks

1.Entity Recognition
    -Identify all key entities in the text, including but not limited to people, locations, organizations, events, dates, items, etc.
    -Assign a unique identifier to each entity (e.g., E1, E2, E3, etc.).

2.Relationship Extraction
    -Identify relationships between entities and represent them in triple form: (Entity1, Relationship, Entity2).
    -For example: (E1, Founder, E2).

3.Attribute Extraction
    -Identify attributes of entities and represent them as key-value pairs: (Entity, Attribute, Value).
    -For example: (E1, Date of Birth, September 10, 1964).
    
##Output Format

Entity List:
E1: Entity Name (Type)  
E2: Entity Name (Type)  
...  

Relationship List:
(E1, Relationship, E2)  
(E3, Relationship, E4)  
...  

Attribute List:
(E1, Attribute, Value)  
(E2, Attribute, Value)  
...  

## Requirements
- Focus on key points only
- Use clear and simple language
- Avoid technical jargon
- Ensure logical flow between sections

Input Text:
{text}

Please provide the response in Simplified Chinese.
"""

MERGE_PROMPT = """

Role: Knowledge Graph Construction Assistant
You are a senior assistant skilled at merging entities, relationships, and attributes from multiple sources for knowledge graph construction.

## Core Tasks
1.Entity Integration
    -Combine entities from all sources, ensuring no duplicates.
    -Assign unique identifiers (e.g., E1, E2, E3) to each entity.
    -Resolve conflicts or inconsistencies in entity naming or categorization.

2.Relationship Integration
    -Merge relationships from all sources into a unified list.
    -Resolve conflicting or redundant relationships.
    -Represent relationships in triple form: (Entity1, Relationship, Entity2).

3.Attribute Integration
    -Combine attributes from all sources, ensuring no duplicates.
    -Resolve conflicts or inconsistencies in attribute values.
    -Represent attributes in key-value pairs: (Entity, Attribute, Value).

## Output Organization
Organize the merged data into the following structured format:
Entity List:
E1: Entity Name (Type)
E2: Entity Name (Type)
...

Relationship List:
(E1, Relationship, E2)
(E3, Relationship, E4)
...

Attribute List:
(E1, Attribute, Value)
(E2, Attribute, Value)
...

## Requirements
    -Ensure consistency in entity naming and categorization.
    -Resolve conflicts or redundancies in relationships and attributes.
    -Maintain logical connections between entities, relationships, and attributes.
    -Preserve all critical information while removing duplicates.
    -Output the final result in a structured and machine-readable format.

Input Text:
{text}

Please provide the response in Simplified Chinese.
"""

FINAL_SUMMARY_PROMPT = """

Role: Knowledge Graph Summary Assistant
You are a senior assistant skilled at creating final summaries of entities, relationships, and attributes for knowledge graph construction.

## Core Tasks
1. Entity Summary
    -Summarize all key entities identified in the input.
    -Highlight the most significant entities and their types (e.g., person, organization, location).
    -Provide a brief description of each entity's role or importance.

2. Relationship Summary
    -Summarize the most important relationships between entities.
    -Represent relationships in triple form: (Entity1, Relationship, Entity2).
    -Highlight relationships that are critical to understanding the overall structure.

3. Attribute Summary
    -Summarize the key attributes associated with entities.
    -Represent attributes in key-value pairs: (Entity, Attribute, Value).
    -Highlight attributes that provide essential context or unique insights.

4. Knowledge Graph Value Analysis
    -Explain the significance of the extracted entities, relationships, and attributes.
    -Discuss how the knowledge graph can be used in practical applications (e.g., data analysis, decision-making).
    -Highlight the potential impact of the knowledge graph in relevant domains.

5.Future Directions
    -Suggest potential improvements or extensions to the knowledge graph.
    -Identify additional entities, relationships, or attributes that could be included.
    -Discuss how the knowledge graph could evolve to support future use cases.

## Requirements
    -Focus on the most important entities, relationships, and attributes.
    -Use clear and concise language.
    -Ensure logical connections between entities, relationships, and attributes.
    -Keep the total length around 1000 words.
    -Provide the response in English.

Input Text:
{text}

Please provide the response in Simplified Chinese.
"""



MIND_MAP_PROMPT = """

Role: Markdown Mindmap Summary Assistant
You are a skilled assistant specialized in summarizing input text into a hierarchical Markdown format, optimized for generating mind maps. Your task is to extract key concepts, sub-concepts, and details from the input text and organize them into a clear and structured Markdown document.

## Core Tasks
1.Extract Main Concepts
    -Identify the main topics or themes in the input text.
    -Represent each main topic as a top-level Markdown heading (#).

2.Extract Sub-Concepts
    -Identify sub-topics or sub-themes related to each main topic.
    -Represent each sub-topic as a second-level Markdown heading (##).

3.Extract Details
    -Identify supporting details, explanations, or examples for each sub-topic.
    -Represent details as third-level Markdown headings (###) or bullet points (-).

4.Organize Hierarchically
    -Ensure the content is organized hierarchically, with clear relationships between main topics, sub-topics, and details.
    -Use the following structure as a template:

# 主要概念  
## 子概念1  
### 详细解释1  
### 详细解释2  
## 子概念2  
### 详细解释3  
# 另一个主要概念  
## 相关内容1  
## 相关内容2  
### 进一步解释  

Requirements
- Focus on the most important concepts and details in the input text.  
- Use clear and concise language.  
- Organize the content hierarchically using Markdown headings (`#`, `##`, `###`).  
- Use bullet points (`-`) for additional details if necessary.  
- Ensure the output is visually clear and easy to convert into a mind map.  
- Keep the total length appropriate for the input text (typically 500-1000 words).  
- Provide the response in Simplified Chinese.  
Input Text:
{text}

Please provide the response in Simplified Chinese.
"""

def get_prompts_type(type: str) -> str:
    """根据传过来的类型返回相应的提示词"""
    if type =="knowledge_graph_extraction_prompt":
        return KNOWLEDGE_GRAPH_EXTRACTION_PROMPT
    elif type == "mind_map_prompt":
        return MIND_MAP_PROMPT

def get_prompts(type: str = "mind_map_prompt") -> Dict[str, str]:
    return {
        "prompt": get_prompts_type(type),
        "merge_prompt": MERGE_PROMPT,
        "final_summary_prompt": FINAL_SUMMARY_PROMPT
    }
