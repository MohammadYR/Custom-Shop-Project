import { Suspense, ComponentType, ReactNode, FC } from "react";

export default function withSuspense<P extends object>(
  Component: ComponentType<P>,
  fallback?: ReactNode,
): FC<P> {
  return (props: P) => (
    <Suspense fallback={fallback}>
      <Component {...props} />
    </Suspense>
  );
}
