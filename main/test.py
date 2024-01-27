import ast
import torch

def check_ast_for_disallowed_operations(node, disallowed_modules, allowed_torch_operations):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name in disallowed_modules:
                raise RuntimeError(f"Disallowed module used: {alias.name}")

    if isinstance(node, ast.ImportFrom):
        if node.module in disallowed_modules:
            raise RuntimeError(f"Disallowed module used: {node.module}")

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
        module_name = node.value.func.value.id
        operation_name = node.value.func.attr
        print(f"Detected PyTorch operation: {module_name}.{operation_name}")
        print(f"Allowed PyTorch operations: {allowed_torch_operations}")
        
        if module_name == 'torch':
            if operation_name not in allowed_torch_operations:
                raise RuntimeError(f"Disallowed PyTorch operation used: {operation_name}")


def run_user_code(user_code):
    # Whitelist of allowed PyTorch operations
    allowed_torch_operations = {
        'argwhere', 'tensor_split', 'gather', 'masked_select', 'movedim', 'splicing',
        't', 'take', 'tile', 'unsqueeze', 'negative', 'positive', 'where', 'remainder',
        'clip', 'argmax', 'argmin', 'sum', 'unique', 'argsort', 'scatter', 'cat',
        'chunk', 'clone', 'contiguous', 'cumprod', 'cumsum', 'diagonal', 'expand',
        'flatten', 'index_select', 'masked_fill', 'masked_scatter', 'narrow', 'permute',
        'repeat', 'reshape', 'roll', 'select', 'split', 'squeeze', 'stack', 't', 'take',
        'transpose', 'unbind', 'unfold', 'unsqueeze', 'view', 'view_as', 'where', 'zero_',
        'randint', 'zeros', 'ones', 'arange'
    }

    # Disallowed modules
    disallowed_modules = {'os', 'subprocess', 'sys'}

    try:
        # Parse the abstract syntax tree
        tree = ast.parse(user_code)

        # Check for disallowed modules and operations in the abstract syntax tree
        for node in ast.walk(tree):
            check_ast_for_disallowed_operations(node, disallowed_modules, allowed_torch_operations)

        exec(user_code)
        return "Success"

    except Exception as e:
        # Handle exceptions, log, and return an error message
        return f"Error during code execution: {str(e)}"
    
def evaluate_code(user_code: str, problem_dict: dict) -> dict:
    """
    Evaluates the user code against the test cases and returns the results
    :param user_code: The user's code
    :param problem_dict: The problem dictionary
    :return: The results of the test cases
    """
    # usercode should change the variable `tensor`
    test_cases = problem_dict["test_cases"]
    num_test_cases = len(test_cases)
    num_test_cases_passed = 0
    result_dict = dict()
    for test_case_id, test_case_dict in enumerate(test_cases):
        # Reset the tensor
        input_string = test_case_dict["input"]
        tensor = torch.tensor(eval(input_string))
        # Run the user code
        try:
            exec(user_code)
        except Exception as e:
            result_dict[test_case_id] = {"status": "error", "error": str(e)}
            continue
        
        test_case_result = dict()
        test_case_result["status"] = "success"
        # Check the output
        output_string = test_case_dict["output"]
        o_tensor = torch.tensor(eval(output_string))

        print("expected: ", o_tensor)
        print("actual: ", tensor)

        if torch.equal(tensor, o_tensor):
            test_case_result["correct"] = True
            num_test_cases_passed += 1
        else:
            test_case_result["correct"] = False
        result_dict[test_case_id] = test_case_result

    ret = dict()
    ret['num_test_cases'] = num_test_cases
    ret['num_test_cases_passed'] = num_test_cases_passed
    ret['result'] = result_dict

    return ret

# Example 1
print("Example 1")
user_provided_code = """
o_tensor = torch.where(tensor == 2, 100, -1)
tensor = o_tensor
"""

problem_dict = {
    "test_cases": [
        {
            "input": "[0]",
            "output": "[-1]",
            "test_case_no": 1
        },
        {
            "input": "[1]",
            "output": "[-1]",
            "test_case_no": 2
        },
        {
            "input": "[0]",
            "output": "[-1]",
            "test_case_no": 3
        },
        {
            "input": "[-3]",
            "output": "[-1]",
            "test_case_no": 4
        },
        {
            "input": "[7]",
            "output": "[-1]",
            "test_case_no": 5
        }
    ]
}

result = evaluate_code(user_provided_code, problem_dict)
print(result)

# Example 2
print("\n\nExample 2")
user_provided_code = """
o_tensor = torch.unique(tensor, dim=1)
tensor = o_tensor
o_tensor = torch.unique(tensor, dim=0)
tensor = o_tensor
"""

problem_dict = {
    "test_cases": [
        {
            "input": "[[-6, -2], [6, 2]]",
            "output": "[[-6, -2], [6, 2]]",
            "test_case_no": 1
        },
        {
            "input": "[[-10, -5], [-1, -8]]",
            "output": "[[-10, -5], [-1, -8]]",
            "test_case_no": 2
        },
        {
            "input": "[[-2, -5], [-10, 1]]",
            "output": "[[-5, -2], [1, -10]]",
            "test_case_no": 3
        },
        {
            "input": "[[9, 2], [9, 2]]",
            "output": "[[2, 9]]",
            "test_case_no": 4
        },
        {
            "input": "[[-6, 8], [-5, -4]]",
            "output": "[[-6, 8], [-5, -4]]",
            "test_case_no": 5
        }
    ]
}

result = evaluate_code(user_provided_code, problem_dict)
print(result)

# Example 3
print("\n\nExample 3")
user_provided_code = """
o_tensor=tensor.clone()
o_tensor[(slice(1, 4, None),)] = torch.positive(o_tensor[(slice(1, 4, None),)])
tensor = o_tensor
o_tensor=tensor.clone()
o_tensor[(slice(2, 4, None),)] = torch.clip(o_tensor[(slice(2, 4, None),)], -4, 4)
tensor = o_tensor
o_tensor=tensor.clone()
o_tensor[(slice(2, 4, None),)] = torch.clip(o_tensor[(slice(2, 4, None),)], -4, 4)
tensor = o_tensor
o_tensor=tensor.clone()
o_tensor[(slice(1, 4, None),)] = torch.clip(o_tensor[(slice(1, 4, None),)], -4, 4)
tensor = o_tensor
"""

problem_dict = {
    "test_cases": [
        {
            "input": "[0, 5, -2, 2]",
            "output": "[0, 4, -2, 2]",
            "test_case_no": 1
        },
        {
            "input": "[-7, 2, 6, -4]",
            "output": "[-7, 2, 4, -4]",
            "test_case_no": 2
        },
        {
            "input": "[-8, 7, 0, -1]",
            "output": "[-8, 4, 0, -1]",
            "test_case_no": 3
        },
        {
            "input": "[-3, 8, 2, -8]",
            "output": "[-3, 4, 2, -4]",
            "test_case_no": 4
        },
        {
            "input": "[3, 5, 3, -7]",
            "output": "[3, 4, 3, -4]",
            "test_case_no": 5
        }
    ]
}

result = evaluate_code(user_provided_code, problem_dict)
print(result)

