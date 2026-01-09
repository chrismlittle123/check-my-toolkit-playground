// File with intentional lint issues for testing

// removed unused variable

export function greet(name: string): string {
  console.log("Hello"); // should trigger no-console warning
  return `Hello, ${name}!`;
}

export function add(a: number, b: number): number {
  return a + b;
}
