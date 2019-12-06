
import React from 'react';
import Modal from './materialize_modal';
import { useForm } from '../forms/forms';
import RoomForm from '../forms/room_form';
import { create_room } from '../zosia_api';

const RoomPropertiesModal = props => {
  const {submit, data} = props
  const [FormInput, formValue, setValue] = useForm(RoomForm, data);
  
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>{data ? "Edit" : "Add"} Room</h4>
        <div className="row">
          <FormInput name="" value={formValue} onChange={setValue}></FormInput>
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-light btn" onClick={() => submit(formValue)}>
          Save
        </a>
      </div>
    </Modal>
  );
}

export default RoomPropertiesModal;
