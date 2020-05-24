import * as React from 'react';

import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

declare const gettext: (messageId: string) => string;

const AddRemoveForms = ({ onAddFilter }: {
  onAddFilter: () => void;
}): JSX.Element => (
  <Form.Group>
    <Button
      onClick={onAddFilter}
      variant="primary"
    >
      {gettext('Agregar filtro')}
    </Button>

    <Button
      className="float-right"
      type="submit"
      variant="success"
    >
      {gettext('Buscar')}
    </Button>
  </Form.Group>
);

export default AddRemoveForms;
