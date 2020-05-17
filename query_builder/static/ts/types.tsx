export interface FilterableField {
  field: string;
  label: string;
  terms: Array<string>;
}

export interface FormDataset {
  query_string: string;
  operator: string;
  filter_on: string;
  filter: string;
  [extraValues: string]: string;
}

export interface SelectProps {
  onChange?: (event: React.FormEvent<HTMLSelectElement>) => void;
  value: string;
}
