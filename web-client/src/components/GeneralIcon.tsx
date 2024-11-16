interface GeneralIconProps {
    children: React.ReactNode
    alt: string
    size?: {
        width?: number
        height?: number
        padding?: number
    }
}

export default function GeneralIcon(props: GeneralIconProps) {
    return (
        <div
            className={`w-fit h-fit inline-flex items-center justify-center "rounded-xl"`}
        >
            <div 
                className="relative h-fit" 
                style={{ 
                    width: props.size ? props.size.width : 25, 
                    height: props.size ? props.size.height : 25, 
                    padding: props.size ? props.size.padding ? props.size.padding : 3.5 : 3.5}}
            >
                {props.children}
            </div>
        </div>
    )
}