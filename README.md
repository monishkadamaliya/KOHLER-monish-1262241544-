# KOHLER AI Bathroom Designer & Planner

An AI-powered bathroom planning system that transforms a user's bathroom space, budget, and design preferences into an optimized bathroom product bundle using verified KOHLER catalogue products.

## 1. Problem Statement

Bathroom product selection requires balancing multiple constraints simultaneously: available space and layout, budget, design theme, product compatibility, and matching finishes. Manually searching a large catalogue and checking these constraints is time-consuming and can lead to incompatible or impractical combinations.

## 2. Proposed Solution

I propose a **hybrid AI + optimization system** that understands the user's requirements and generates a feasible bathroom product bundle.

The system:
- Understands bathroom dimensions, layout/image, budget, and preferred theme.
- Converts user input into structured design requirements.
- Retrieves candidate products from the verified KOHLER catalogue.
- Applies compatibility, finish, dimensional, and budget constraints.
- Optimizes the remaining products into a coherent bundle.
- Returns real catalogue SKUs with an explainable selection rationale.

**Core rule:** The AI does not invent SKUs, prices, or product specifications. Recommendations are grounded in the structured catalogue.

## 3. Key Innovation

### Hybrid AI + Deterministic Decision Making

Instead of allowing an LLM to directly choose products, the system separates **requirement understanding** from **product validation and optimization**.

**AI / Amazon Bedrock + Nova:**
- Natural-language requirement understanding
- Design-theme interpretation
- Image understanding
- Recommendation explanation

**Deterministic engines:**
- SKU and catalogue validation
- Dimension constraints
- Finish matching
- Product compatibility
- Budget constraints
- Final optimization

This architecture combines the flexibility of generative AI with the reliability of rule-based catalogue validation and optimization.

## 4. User Workflow

```text
User Input
  │
  ├── Bathroom Dimensions / Layout / Image
  ├── Budget
  └── Design Theme
          │
          ▼
AI Requirement Understanding
          │
          ▼
Structured Design Requirements
          │
          ▼
Catalogue Retrieval
          │
          ▼
Compatibility + Finish Filtering
          │
          ▼
Budget + Space Optimization
          │
          ▼
Verified KOHLER Product Bundle
          │
          ▼
Design Summary + Explanation
```

Supported themes:
- **Minimalist Modern**
- **Classic Luxury**
- **Japanese Zen**

## 5. System Architecture

```text
                    ┌─────────────────────┐
                    │      FRONTEND       │
                    │ User Input & Results│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      BACKEND API    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Amazon Bedrock /    │
                    │ Amazon Nova         │
                    │ Requirement + Image │
                    │ Understanding      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Structured Intent   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
     ┌──────────────────┐             ┌──────────────────┐
     │ Catalogue Engine │             │     ChromaDB     │
     │ Exact catalogue  │             │ Semantic product│
     │ data + validation│             │ retrieval        │
     └────────┬─────────┘             └────────┬─────────┘
              └────────────────┬────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Compatibility +     │
                    │ Finish Engine       │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Optimization Engine │
                    │ Space + Budget +    │
                    │ Theme + Compatibility│
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Verified KOHLER     │
                    │ SKUs + Explanation  │
                    └─────────────────────┘
```

## 6. Compatibility Engine

The compatibility engine ensures that products selected for a bathroom can work together before they reach the final optimization stage.

```text
Candidate Products
       │
       ▼
Category Compatibility
       │
       ▼
Dimension / Space Constraints
       │
       ▼
Specification Compatibility
       │
       ▼
Finish Compatibility
       │
       ▼
Compatible Product Set
```

A **FinishMapper** normalizes catalogue finish names into finish families and checks whether selected products can form a visually consistent finish combination.

Compatibility is treated as a **hard constraint**: products that fail required compatibility checks are removed rather than being recommended with a warning.

## 7. Optimization Strategy

The optimizer searches for a feasible product bundle while respecting hard constraints and maximizing user preferences.

### Hard Constraints
- Budget limit
- Available bathroom space
- Required product categories
- Product compatibility
- Valid catalogue SKU

### Soft Objectives
- Theme alignment
- Finish consistency
- User preferences
- Feature suitability
- Overall bundle quality

```text
Hard Constraints
Budget + Space + Compatibility
            │
            ▼
Candidate Bundles
            │
            ▼
Preference / Theme Scoring
            │
            ▼
Constraint-Based Optimization
            │
            ▼
Best Feasible Bundle
```

The optimization layer is deterministic and operates only on validated catalogue data.

## 8. Image Processing Pipeline

When the user provides a bathroom image, the image is processed before product optimization.

```text
Bathroom Image
      │
      ▼
Image Understanding
      │
      ├── Approximate Layout
      ├── Visible Fixtures
      ├── Visible Finishes / Materials
      └── Spatial Constraints
      │
      ▼
Structured Room Representation
      │
      ▼
Design Requirements
      │
      ▼
Catalogue Retrieval
      │
      ▼
Compatibility + Optimization
```

Image analysis provides **design and spatial cues**, not unsupported exact measurements. Dimensions supplied directly by the user remain the authoritative source for precise space constraints.

## 9. Example End-to-End Case

### Input

```text
Theme: Classic Luxury
Budget: User-defined budget
Bathroom: User-provided dimensions + bathroom image
Required categories:
- Faucet
- Smart Toilet
- Thermostatic Shower
- Vanity
```

### Processing

```text
User Requirements
       ↓
AI extracts structured intent
       ↓
Real KOHLER catalogue candidates retrieved
       ↓
Invalid / incompatible products removed
       ↓
FinishMapper checks finish consistency
       ↓
Budget + space constraints applied
       ↓
Optimization engine evaluates feasible bundles
       ↓
Final verified catalogue bundle
```

### Output

The system returns a bundle containing **real catalogue SKUs**, product names, prices, finishes, compatibility information, and a concise explanation of why the combination satisfies the user's requirements.

The same pipeline can be applied to **Minimalist Modern** and **Japanese Zen** designs by changing the user's design intent and preference constraints.

---

**KOHLER–MITWPU AI Research Lab Program | Track 1: AI Bathroom Designer & Planner**
