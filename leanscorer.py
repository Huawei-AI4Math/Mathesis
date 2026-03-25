import json
import time
from datetime import datetime
import requests
import re
from itertools import combinations
import math

# Configuration
API_KEY = 'API_KEY'
BASE_URL = 'BASE_URL'
MODEL_NAME = 'MODEL_NAME'

REQUEST_TIMEOUT = 60.0  # Seconds


def call_api(prompt, entity_id):
    """Make a synchronous API call"""
    try:
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT
        )

        elapsed = time.time() - start_time

        if response.status_code != 200:
            error_msg = f"API error {response.status_code}: {response.text}"
            print(f"API call failed for {entity_id}: {error_msg}")
            return {"error": error_msg}

        print(f"API call for {entity_id} completed in {elapsed:.2f}s")
        return {
            "response": response.json()["choices"][0]["message"]["content"],
            "usage": response.json().get("usage", {})
        }
    except Exception as e:
        error_msg = f"Exception in API call for {entity_id}: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


def create_first_prompt(informal_prefix_en: str) -> str:
    """Create the first prompt for deriving mathematical condition from informal description"""
    one_shot = r'''Help me list the conditions and conclusions in this problem (using specific mathematical formulas), without solving it:

Here is an example:
[Problem]: The sequence $\{a_n\}$ satisfies $a_1 = 1$, $a_2 = 2$, $a_{n + 2}=2a_{n + 1}-a_n + 2$. Let $b_n=a_{n + 1}-a_n$. Prove that $\{b_n\}$ is an arithmetic sequence.  

[Conditions and Conclusions]:  
Conditions:  
1. $a_1 = 1$  
2. $a_2 = 2$  
3. $\forall n \geq 1, a_{n + 2} = 2a_{n + 1} - a_n + 2$  
4. $\forall n \geq 1, b_n = a_{n + 1} - a_n$  

Conclusion:  
- $\{b_n\}$ is an arithmetic sequence, i.e., $\exists d \in \mathbb{R}, \forall n \geq 1, b_{n + 1} - b_n = d$.  

'''

    prompt = f'''Now, please help me extract the conditions and conclusions for this problem in the same way (using specific mathematical formulas), without solving it:  
[Problem]: {informal_prefix_en}

[Conditions and Conclusions]:
'''

    return one_shot + prompt


def create_second_prompt(informal_prefix_en, math_cond: str, formal_statement: str) -> str:
    """Create the second prompt for assessing appropriateness of formal statement"""

    theorem_index = formal_statement.find("theorem ")
    if theorem_index != -1:
        formal_statement = formal_statement[theorem_index:]

    one_shot = r"""Let's compare the mathematical conditions and conclusions with the Lean 4 formal statement one by one:

1. **\( q \) is a natural number greater than 1**:  
   - Math: \( q \in \mathbb{N}, q > 1 \).  
   - Lean: `(hq : 1 < q)`.  
   - Match: \box{Perfectly match}.

2. **\( n \) is a natural number greater than 1**:  
   - Math: \( n \in \mathbb{N}, n > 1 \).  
   - Lean: `(hn : 1 < n)`.  
   - Match: \box{Perfectly match}.

3. **Set \( M = \{0, 1, 2, \cdots, q - 1\} \)**:  
   - Math: \( M \) is explicitly defined as this set.  
   - Lean: `(M : Finset ℕ := Finset.range q)`.  
   - Detailed interpretation: `Finset.range q` is `{0, 1, ..., q - 1}`.  
   - Match: \box{Perfectly match}.

4. **Set \( A \) definition**:  
   - Math: \( A = \{x \vert x = \sum_
    {i = 1} ^ n
    x_i
    q ^ {i - 1}, x_i \ in M\} \).
   - Lean: `A : Set ℕ := {x | ∃ (x_vec : ℕ → ℕ), (∀ i, x_vec i ∈ M) ∧ x = ∑ i in Finset.range
    n, x_vec(i + 1) * q ^ i}`.
   - Detailed interpretation: In Lean, `x_vec` is indexed from `1` to `n` (since `i + 1` ranges from `1` to `n`), but the math defines \( x_i \) for \( i = 1, 2, \cdots, n \). This is actually consistent, but the Lean representation is slightly more general (allowing `x_vec` to be a function on all naturals, but only using `x_vec (i + 1)` for `i` in `Finset.range n`). The Lean definition is technically correct but slightly more abstract than the math. However, it captures the same idea.
   - Match: \box{Minor inconsistency}.

5. **\( s, t \in A \) with specific expansions**:
   - Math: \( s = \sum_{i = 1}^n a_i q^{i - 1} \), \( t = \sum_{i = 1}^n b_i q^{i - 1} \), with \( a_i, b_i \in M \).
   - Lean: `s = ∑ i in Finset.range n, a (i + 1) * q ^ i`, `t = ∑ i in Finset.range n, b (i + 1) * q ^ i`, with `∀ i, a i ∈ M` and `∀ i, b i ∈ M`.
   - Detailed interpretation: The Lean version uses `a (i + 1)` and `b (i + 1)` to match the indexing in the sum, which is equivalent to the math but slightly indirect. The math directly uses \( a_i \) for \( i = 1, \dots, n \), while Lean uses `a i` for all `i` but only evaluates at `i + 1`. The Lean version is correct but not a literal translation.
   - Match: \box{Minor inconsistency}.

6. **\( a_n < b_n \)**:  
   - Math: \( a_n < b_n \).
   - Lean: `(hab : a n < b n)`.
   - Match: \box{Perfectly match}.

7. **Conclusion \( s < t \)**:
   - Math: \( s < t \).
   - Lean: `s <= t`.
   - Match: \box{Major inconsistency}.

### Check for missing conditions / implicit conditions:
   - No missing conditions / implicit conditions
   - Match: \box{Perfectly match}.
"""

    prompt = f"""Here is a math question and a lean 4 statement. Compare the conditions and conclusions in this code with the mathematical ones, matching them one by one to see if the formal statement is an appropriate translation of the mathematical condition by assigning one of three tags (Perfectly match; Minor inconsistency; Major inconsistency). Then, audit for missing/implicit conditions.  Judge with extremely strict standards—any minor inconsistency will be considered a mismatch. Special attention to triangle angle-side correspondence. If the question explicitly mentions "opposite angles/sides", this correspondence must be clearly stated and correct.
**Stop immediately** after evaluating all pairs. Do **not** summarize or analyze further. 

Output Format:
{one_shot}

-----------------

Question: 
{informal_prefix_en}

Mathematical conditions and conclusions:
{math_cond}

Lean 4 formal statement:
{formal_statement}

Output:
"""
    return prompt


def extract_box_content(text):
    """Extract content from \box{} patterns and convert to evaluation scores"""
    box_mapping = {
        'Perfectly match': 'A',
        'Minor inconsistency': 'B',
        'Major inconsistency': 'C'
    }

    matches = re.findall(r'\\box{([^}]*)}', str(text))
    converted = []
    for match in matches:
        cleaned = match.strip()
        for key, value in box_mapping.items():
            if key.lower() in cleaned.lower():
                converted.append(value)
                break
        else:
            converted.append(None)
    return converted


def generate_mu(evaluations):
    """
    Dynamically generate fuzzy measure mu(A) with rules:
    1. If A contains any C, mu(A)=0.
    2. If A contains all subtasks and all are A, mu(A)=1.0.
    3. If A contains 2+ Bs, mu(A) = base_weight * (1 - 0.2 * B_count).
    4. Otherwise: mu(A) = sum(individual subtask weights) / total subtasks.
    """
    n = len(evaluations)
    if n > 10:
        # calculate the proportion for A
        a_count = float(evaluations.count('A')) / n

        a_count = int(math.floor(a_count * 10))  # round down to the nearest integer
        b_count = 10 - a_count

        print(f'evaluations before: {evaluations}')

        n = 10  # set n to 10
        # new an evaluations array with 10 elements
        evaluations = []
        for i in range(a_count):
            evaluations.append('A')
        for i in range(b_count):
            evaluations.append('B')

        print(f'evaluations after: {evaluations}')


    mu = {}
    all_tasks = frozenset(range(n))
    base_weight = 1.0 / n

    C_tag = False
    if any(evaluations[i] == 'C' for i in range(n)):
        C_tag = True

    for k in range(1, n + 1):
        for subset in combinations(range(n), k):
            A = frozenset(subset)
            # Rule 1: If A contains any C, mu(A)=0
            if C_tag:
                mu[A] = 0.0
            else:
                # Rule 2: All-A subset weight=1.0
                if A == all_tasks and all(evaluations[i] == 'A' for i in A):
                    mu[A] = 1.0
                else:
                    b_count = sum(1 for i in A if evaluations[i] == 'B')
                    # Rule 3: Penalize weight for 2+ Bs
                    if b_count >= 2:
                        mu[A] = max(base_weight * len(A) * (1 - 0.2 * b_count), 0)
                    else:
                        # Rule 4: Default basic weight sum
                        mu[A] = base_weight * len(A) * (1 - 0.1 * b_count)
    return mu, evaluations


def sugeno_integral(evaluations):
    """
    Strictly ensure score is 0 when C exists:
    1. If any subtask is C, return 0 directly.
    2. Otherwise calculate Sugeno integral normally.
    """
    if not evaluations:
        return 0.0

    mu,evaluations = generate_mu(evaluations)

    grade_map = {'A': 1.0, 'B': 0.5, "C": 0}
    f = [grade_map[e] for e in evaluations if e in grade_map]

    if not f:  # If no valid evaluations after filtering
        return 0.0

    n = len(f)
    print(f"n={n}")

    sorted_indices = sorted(range(n), key=lambda i: f[i])
    sugeno = 0.0
    for i in range(n):
        A = frozenset(sorted_indices[i:])
        mu_A = mu.get(A, 0.0)
        sugeno = max(sugeno, min(f[sorted_indices[i]], mu_A))

    return round(sugeno, 2)



def process_question(translated_question, formal_statement):
    """Process a single question through the complete pipeline"""
    print(f"Starting processing at {datetime.now()}")

    # Validate inputs
    if not translated_question or not translated_question.strip():
        return {"error": "Missing translated_question"}

    if not formal_statement or not formal_statement.strip():
        return {"error": "Missing formal_statement"}

    # Step 1: Get mathematical conditions from translated_question
    print("Step 1: Creating first prompt for mathematical conditions...")
    first_prompt = create_first_prompt(translated_question)
    print("First prompt created. Making API call...")

    first_result = call_api(first_prompt, "step1_conditions")

    if "error" in first_result:
        return {"error": f"Step 1 failed: {first_result['error']}"}

    math_cond = first_result["response"]
    print("Step 1 completed successfully")
    print(f"Mathematical conditions extracted:\n{math_cond}\n")

    # Step 2: Compare formal statement with mathematical conditions
    print("Step 2: Creating second prompt for evaluation...")
    second_prompt = create_second_prompt(translated_question, math_cond, formal_statement)
    print("Second prompt created. Making API call...")

    second_result = call_api(second_prompt, "step2_evaluation")

    if "error" in second_result:
        return {
            "error": f"Step 2 failed: {second_result['error']}",
            "prompt1_output": math_cond
        }

    prompt2_output = second_result["response"]
    print("Step 2 completed successfully")
    print(f"Evaluation output:\n{prompt2_output}\n")

    # Step 3: Extract evaluations and calculate score
    print("Step 3: Extracting evaluations and calculating score...")
    conclusions = extract_box_content(prompt2_output)
    lean_score = sugeno_integral(conclusions)

    print(f"Evaluations extracted: {conclusions}")
    print(f"Final lean score: {lean_score}")
    print(f"Pass status: {lean_score >= 0.6}")

    # Return complete result
    result = {
        "translated_question": translated_question,
        "formal_statement": formal_statement,
        "prompt1_output": math_cond,
        "prompt2_output": prompt2_output,
        "lean_score": lean_score,
        "pass": lean_score >= 0.6,
        "evaluations": ",".join([str(e) for e in conclusions if e is not None]),
        "error": ""
    }

    return result


def main():
    # Input strings - replace these with your actual data
    translated_question = r"""For a function $f(x)$ and a point $M(a, b)$, let $s(x)=(x-a)^2+(f(x)-b)^2$. If $P\left(x_0, f\left(x_0\right)\right)$ is the point where $s(x)$ attains its minimum, then point $P$ is called the "closest point" of $M$ on $f(x)$. For $f(x)=\frac{1}{x}(x>0)$, prove that for the point $M(0,0)$, there exists a point $P$ such that $P$ is the "closest point" of $M$ on $f(x)$."""

    formal_statement = r"""theorem default_data_id  (f : ℝ → ℝ) (hf : f = fun x => 1 / x) (M : ℝ × ℝ) (hM : M = (0, 0)) :
    ∃ P : ℝ × ℝ, P.1 > 0 ∧ P.2 = f P.1 ∧
    (∀ x, x > 0 → (x - M.1)^2 + (f x - M.2)^2 ≥
      (P.1 - M.1)^2 + (P.2 - M.2)^2) := by sorry """

    print("=" * 60)
    print("LEAN STATEMENT EVALUATION PIPELINE")
    print("=" * 60)
    print(f"Input Question: {translated_question}")
    print(f"Formal Statement: {formal_statement}")
    print("=" * 60)

    # Process the question
    result = process_question(translated_question, formal_statement)

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Lean Score: {result['lean_score']}")
        print(f"Pass: {result['pass']}")
        print(f"Evaluations: {result['evaluations']}")

    print("=" * 60)
    return result


if __name__ == "__main__":
    main()