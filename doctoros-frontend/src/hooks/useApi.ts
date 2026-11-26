import { useCallback, useEffect, useState, type DependencyList } from 'react';
import { getErrorMessage, getStatus } from '@/api/client';

interface State<T> { data: T | null; error: string | null; status?: number; loading: boolean }

/** Generic loading/error/data hook. Components never call axios directly. */
export function useApi<T>(fn: () => Promise<T>, deps: DependencyList) {
  const [state, setState] = useState<State<T>>({ data: null, error: null, loading: true });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((data) => live && setState({ data, error: null, loading: false }))
      .catch((e: unknown) => live && setState({ data: null, error: getErrorMessage(e), status: getStatus(e), loading: false }));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { ...state, reload };
}
