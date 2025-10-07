#!/bin/bash
# Validate GitHub Actions workflows
# This script checks YAML syntax and workflow structure

set -e

echo "🔍 Validating GitHub Actions Workflows..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Create temporary Python script for YAML validation
cat > /tmp/validate_yaml.py << 'EOF'
import sys
import yaml
import json

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Check for common workflow issues
        issues = []

        # Check if it's a workflow file
        if 'on' not in data and 'true' not in str(data):
            issues.append("Missing 'on' trigger definition")

        if 'jobs' not in data:
            issues.append("Missing 'jobs' definition")

        # Check for job structure
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if 'runs-on' not in job_config:
                    issues.append(f"Job '{job_name}' missing 'runs-on'")
                if 'steps' not in job_config:
                    issues.append(f"Job '{job_name}' missing 'steps'")

        return True, issues
    except yaml.YAMLError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [str(e)]

if __name__ == '__main__':
    file_path = sys.argv[1]
    valid, issues = validate_yaml(file_path)

    result = {
        'valid': valid,
        'issues': issues
    }
    print(json.dumps(result))
EOF

# Validate workflow files
WORKFLOW_DIR=".github/workflows"
VALID=true

if [ ! -d "$WORKFLOW_DIR" ]; then
    echo -e "${RED}❌ Workflow directory not found: $WORKFLOW_DIR${NC}"
    exit 1
fi

echo "📁 Checking workflow files in $WORKFLOW_DIR"
echo ""

for workflow in "$WORKFLOW_DIR"/*.yml; do
    if [ -f "$workflow" ]; then
        filename=$(basename "$workflow")
        echo -n "  Validating $filename... "

        # Validate YAML
        result=$(python3 /tmp/validate_yaml.py "$workflow")
        valid=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['valid'])")
        issues=$(echo "$result" | python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin)['issues']))")

        if [ "$valid" == "True" ]; then
            if [ -z "$issues" ]; then
                echo -e "${GREEN}✅ Valid${NC}"
            else
                echo -e "${YELLOW}⚠️  Valid with warnings${NC}"
                echo "$issues" | while read -r line; do
                    echo -e "    ${YELLOW}Warning: $line${NC}"
                done
            fi
        else
            echo -e "${RED}❌ Invalid${NC}"
            echo "$issues" | while read -r line; do
                echo -e "    ${RED}Error: $line${NC}"
            done
            VALID=false
        fi
    fi
done

echo ""

# Validate dependabot.yml
echo "📁 Checking Dependabot configuration"
echo ""

DEPENDABOT_FILE=".github/dependabot.yml"
if [ -f "$DEPENDABOT_FILE" ]; then
    echo -n "  Validating dependabot.yml... "

    result=$(python3 /tmp/validate_yaml.py "$DEPENDABOT_FILE")
    valid=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['valid'])")

    if [ "$valid" == "True" ]; then
        echo -e "${GREEN}✅ Valid${NC}"
    else
        echo -e "${RED}❌ Invalid${NC}"
        echo "$result" | python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin)['issues']))"
        VALID=false
    fi
else
    echo -e "  ${YELLOW}⚠️  dependabot.yml not found${NC}"
fi

echo ""

# Check pre-commit config
echo "📁 Checking Pre-commit configuration"
echo ""

PRECOMMIT_FILE=".pre-commit-config.yaml"
if [ -f "$PRECOMMIT_FILE" ]; then
    echo -n "  Validating .pre-commit-config.yaml... "

    result=$(python3 /tmp/validate_yaml.py "$PRECOMMIT_FILE")
    valid=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['valid'])")

    if [ "$valid" == "True" ]; then
        echo -e "${GREEN}✅ Valid${NC}"
    else
        echo -e "${RED}❌ Invalid${NC}"
        VALID=false
    fi
else
    echo -e "  ${YELLOW}⚠️  .pre-commit-config.yaml not found${NC}"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$VALID" = true ]; then
    echo -e "${GREEN}✅ All workflows are valid!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Commit the workflow files"
    echo "  2. Push to GitHub"
    echo "  3. Check Actions tab for workflow runs"
    echo "  4. Set up branch protection rules"
    exit 0
else
    echo -e "${RED}❌ Some workflows have errors${NC}"
    echo ""
    echo "Please fix the errors above before committing."
    exit 1
fi
