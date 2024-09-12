import { AxiosError } from "axios";
import { toast } from "react-toastify";

export const handleError = (error: AxiosError) => {
  console.log(error);
  if (error.response) {
    if (error.response.data) {
      console.log(error.response.data);

      // if response data is a dictionary, parse it as key=value
      if (typeof error.response.data === 'object') {
        let errorString = '';
        for (const key in error.response.data) {
          let value = parseValue(error.response.data[key]);
          errorString += `${key}: ${value}\n`;
        }
        toast.error(`Error: ${errorString}`);
        return;
      }

      toast.error(`Error: ${JSON.stringify(error.response.data)}`);
      return
    }
  } else {
    toast.error(`Error: ${JSON.stringify(error.message)}`);
    return;
  }
}

const parseValue = (value: any) => {
  if (typeof value === 'string') {
    // remove \" from string
    value = value.replace(/\"/g, '');
    value = value.replace(/"/g, '');
    return value;
  }
  
  if (Array.isArray(value)) {
    let parsedValue = '';
    value.forEach((v) => {
      parsedValue += parseValue(v);
    });
    return parsedValue;
  }

  if (typeof value === 'object') {
    return JSON.stringify(value);
  } 

  return value;
}