import { cn } from "@/lib/utils";
import { Tooltip } from "@mui/material";

export interface InputLabelProps {
  tooltip: string;
  label: string;
  required?: boolean
  className?: string;
}

const InputLabel: React.FC<InputLabelProps> = (props) => {
  const { tooltip, label } = props;
  const isRequired = props.required ? <span className="text-red">*</span> : null;

  return ( 
    <Tooltip title={tooltip}>
      <div className={cn("input-group-prepend", props.className)}>
        <div className="input-group-text rounded-0" id="basic-addon1">
          <span>{label}</span>{isRequired}
        </div>
      </div>
    </Tooltip>
   );
}
 
export default InputLabel;