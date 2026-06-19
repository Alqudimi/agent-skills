# Engineering Best Practices

This document provides detailed guidelines for applying the fundamental engineering principles required by the "Intelligent Systems Architect" skill.

## 1. The Five-Pillar Balance

When designing or implementing any system, a delicate balance must be maintained between the following five pillars:

1.  **Performance**: Improve response speed and resource consumption efficiency. Avoid unnecessary operations, use appropriate data structures, and group logical commands to reduce time.
2.  **Security**: Protect the system from vulnerabilities and intrusions. Treat all inputs as untrusted, and apply the Principle of Least Privilege.
3.  **Maintainability/Developability**: Write clean, organized, and well-documented code. Use clear variable names, and divide code into independent modules (Modularization).
4.  **Usability**: Design intuitive interfaces and interactions for the end-user. Provide clear and helpful error messages.
5.  **Scalability**: Design the system to handle increased load or new features in the future without requiring a complete rewrite.

## 2. Root Cause Analysis (RCA)

When encountering a problem or error, do not merely address superficial symptoms. Follow these steps to reach the root cause:

1.  **Clearly Define the Problem**: What exactly is the error? When does it occur?
2.  **Gather Data**: Examine error logs, error messages, and execution context.
3.  **Ask "Why?" (The 5 Whys)**: Repeatedly ask "Why did this happen?" until you reach the underlying cause.
    *   *Example*: Why did the application crash? (Because the database is offline) -> Why is it offline? (Because the network service stopped) -> Why did it stop? (Due to memory exhaustion) -> Why was memory exhausted? (Due to a memory leak in the image processing module).
4.  **Implement the Root Solution**: Address the underlying cause (in the example: fix the memory leak) instead of merely restarting the service.

## 3. Planning and Decomposition

Do not start direct implementation of complex tasks. Follow this approach:

1.  **Define the Final Objective**: What is the desired outcome? What are the success criteria?
2.  **Phasing**: Divide the large task into 3-5 main phases.
3.  **Modularization**: Within each phase, divide the work into independent logical units that can be tested separately.
4.  **Phased Verification**: Do not move to the next phase until the current phase is completely and correctly finished.

## 4. Dependency Management

*   **Minimum Necessary**: Do not install any library or tool unless it is absolutely essential and the goal cannot be easily achieved without it.
*   **Reliability**: Verify that the libraries used are well-supported, not deprecated, and have an active community.
*   **Compatibility**: Ensure that library versions are compatible with the current language versions and environment before installation.

## 5. Execution Efficiency

*   **Command Grouping**: Instead of executing multiple `shell` commands separately, group them using `&&` or write a small script to execute them in one go.
*   **Direct Solutions**: Always look for the simplest and most direct solution. Avoid "magical" or unnecessarily complex solutions.
