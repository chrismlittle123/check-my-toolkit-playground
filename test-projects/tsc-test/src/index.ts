// TypeScript file with type errors for testing

function greet(name: string): string {
  const unusedVar = "test"; // noUnusedLocals should catch this
  return `Hello, ${name}!`;
}

function add(a: number, b: number, c: number): number {
  // c is unused - noUnusedParameters should catch this
  return a + b;
}

// Type error - string assigned to number
const num: number = "not a number";

export { greet, add };
