#!/bin/bash

# Custom Subagent Creator Script for Linux/Mac
# Usage: ./create-agent.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Available categories
CATEGORIES=("frontend" "backend" "devops" "documentation" "business" "fullstack")

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}  Custom Subagent Creator${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Function to display categories
show_categories() {
    echo -e "${YELLOW}Available categories:${NC}"
    for i in "${!CATEGORIES[@]}"; do
        echo "  $((i+1)). ${CATEGORIES[$i]}"
    done
}

# Get agent name
read -p "Enter agent name (e.g., 'my-custom-agent'): " AGENT_NAME
if [ -z "$AGENT_NAME" ]; then
    echo -e "${RED}Error: Agent name cannot be empty${NC}"
    exit 1
fi

# Get category
echo ""
show_categories
read -p "Select category (1-${#CATEGORIES[@]}): " CATEGORY_INDEX

if ! [[ "$CATEGORY_INDEX" =~ ^[0-9]+$ ]] || [ "$CATEGORY_INDEX" -lt 1 ] || [ "$CATEGORY_INDEX" -gt "${#CATEGORIES[@]}" ]; then
    echo -e "${RED}Error: Invalid category selection${NC}"
    exit 1
fi

CATEGORY="${CATEGORIES[$((CATEGORY_INDEX-1))]}"

# Get other details
echo ""
read -p "Enter agent description: " AGENT_DESCRIPTION
read -p "Enter agent type (e.g., 'generator', 'analyzer', 'optimizer'): " AGENT_TYPE
read -p "Enter author name: " AUTHOR

# Create agent directory
AGENT_DIR="./agents/$CATEGORY/$AGENT_NAME"

if [ -d "$AGENT_DIR" ]; then
    echo -e "${RED}Error: Agent directory already exists: $AGENT_DIR${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Creating agent directory: $AGENT_DIR${NC}"
mkdir -p "$AGENT_DIR/examples"

# Copy and process templates
echo -e "${YELLOW}Generating files from templates...${NC}"

# Process agent.json
sed -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
    -e "s/{{AGENT_TYPE}}/$AGENT_TYPE/g" \
    -e "s/{{AGENT_DESCRIPTION}}/$AGENT_DESCRIPTION/g" \
    -e "s/{{CATEGORY}}/$CATEGORY/g" \
    -e "s/{{AUTHOR}}/$AUTHOR/g" \
    -e "s/{{CAPABILITY_1}}/Capability 1/g" \
    -e "s/{{CAPABILITY_2}}/Capability 2/g" \
    -e "s/{{CAPABILITY_3}}/Capability 3/g" \
    -e "s/{{TAG_1}}/tag1/g" \
    -e "s/{{TAG_2}}/tag2/g" \
    -e "s/{{TAG_3}}/tag3/g" \
    -e "s/{{EXAMPLE_TITLE}}/Example Usage/g" \
    -e "s/{{EXAMPLE_DESCRIPTION}}/Basic example/g" \
    -e "s/{{EXAMPLE_INPUT}}/Sample input/g" \
    -e "s/{{EXAMPLE_OUTPUT}}/Sample output/g" \
    "./templates/agent-template/agent.json.template" > "$AGENT_DIR/agent.json"

# Process README.md
sed -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
    -e "s/{{AGENT_DESCRIPTION}}/$AGENT_DESCRIPTION/g" \
    -e "s/{{CATEGORY}}/$CATEGORY/g" \
    -e "s/{{CAPABILITY_1}}/Capability 1/g" \
    -e "s/{{CAPABILITY_2}}/Capability 2/g" \
    -e "s/{{CAPABILITY_3}}/Capability 3/g" \
    -e "s/{{EXAMPLE_USAGE}}/Add your example here/g" \
    -e "s/{{ADVANCED_EXAMPLE}}/Add your advanced example here/g" \
    -e "s/{{INPUT_FORMAT}}/Describe input format/g" \
    -e "s/{{OUTPUT_FORMAT}}/Describe output format/g" \
    -e "s/{{BEST_PRACTICE_1}}/Best practice 1/g" \
    -e "s/{{BEST_PRACTICE_2}}/Best practice 2/g" \
    -e "s/{{BEST_PRACTICE_3}}/Best practice 3/g" \
    -e "s/{{LIMITATION_1}}/Limitation 1/g" \
    -e "s/{{LIMITATION_2}}/Limitation 2/g" \
    -e "s/{{AUTHOR}}/$AUTHOR/g" \
    "./templates/agent-template/README.md.template" > "$AGENT_DIR/README.md"

# Process prompt.md
sed -e "s/{{AGENT_NAME}}/$AGENT_NAME/g" \
    -e "s/{{AGENT_PURPOSE}}/your custom purpose/g" \
    -e "s/{{EXPERTISE_1}}/Expertise area 1/g" \
    -e "s/{{EXPERTISE_2}}/Expertise area 2/g" \
    -e "s/{{EXPERTISE_3}}/Expertise area 3/g" \
    -e "s/{{OBJECTIVE_1}}/Objective 1/g" \
    -e "s/{{OBJECTIVE_2}}/Objective 2/g" \
    -e "s/{{OBJECTIVE_3}}/Objective 3/g" \
    -e "s/{{ANALYSIS_STEP_1}}/Analysis step 1/g" \
    -e "s/{{ANALYSIS_STEP_2}}/Analysis step 2/g" \
    -e "s/{{EXECUTION_STEP_1}}/Execution step 1/g" \
    -e "s/{{EXECUTION_STEP_2}}/Execution step 2/g" \
    -e "s/{{VALIDATION_STEP_1}}/Validation step 1/g" \
    -e "s/{{VALIDATION_STEP_2}}/Validation step 2/g" \
    -e "s/{{OUTPUT_STANDARD_1}}/Output standard 1/g" \
    -e "s/{{OUTPUT_STANDARD_2}}/Output standard 2/g" \
    -e "s/{{OUTPUT_STANDARD_3}}/Output standard 3/g" \
    -e "s/{{ACCURACY_GUIDELINE}}/Accuracy guideline/g" \
    -e "s/{{COMPLETENESS_GUIDELINE}}/Completeness guideline/g" \
    -e "s/{{CONSISTENCY_GUIDELINE}}/Consistency guideline/g" \
    -e "s/{{ERROR_HANDLING_1}}/Error handling step 1/g" \
    -e "s/{{ERROR_HANDLING_2}}/Error handling step 2/g" \
    -e "s/{{ERROR_HANDLING_3}}/Error handling step 3/g" \
    -e "s/{{CONSTRAINT_1}}/Constraint 1/g" \
    -e "s/{{CONSTRAINT_2}}/Constraint 2/g" \
    -e "s/{{CONSTRAINT_3}}/Constraint 3/g" \
    -e "s/{{SUCCESS_CRITERIA_1}}/Success criteria 1/g" \
    -e "s/{{SUCCESS_CRITERIA_2}}/Success criteria 2/g" \
    -e "s/{{SUCCESS_CRITERIA_3}}/Success criteria 3/g" \
    "./templates/agent-template/prompt.md.template" > "$AGENT_DIR/prompt.md"

# Create example file
cat > "$AGENT_DIR/examples/example1.md" << EOF
# Example 1: Basic Usage

## Input
\`\`\`
Add your example input here
\`\`\`

## Process
1. Step 1
2. Step 2
3. Step 3

## Output
\`\`\`
Add your example output here
\`\`\`
EOF

echo ""
echo -e "${GREEN}✓ Agent created successfully!${NC}"
echo ""
echo -e "${BLUE}Agent Details:${NC}"
echo "  Name: $AGENT_NAME"
echo "  Category: $CATEGORY"
echo "  Type: $AGENT_TYPE"
echo "  Location: $AGENT_DIR"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Edit $AGENT_DIR/prompt.md to define agent behavior"
echo "  2. Update $AGENT_DIR/README.md with detailed documentation"
echo "  3. Customize $AGENT_DIR/agent.json with specific tools and capabilities"
echo "  4. Add usage examples in $AGENT_DIR/examples/"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
