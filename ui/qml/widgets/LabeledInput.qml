import QtQuick 2.9

Row {
    id: labeledInput

    property variant key
    property alias value: textfield.text

    signal changed(string value)

    spacing: 6
    anchors { right: parent.right }
    anchors { leftMargin: 2; rightMargin: 2 }

    Text {
        color: "#eeeeee"
        font.pixelSize: 10
        text: key + ": "
    }

    Rectangle {
        color: "#444444"
        TextInput {
            id: textfield
            anchors.fill: parent
            font.pixelSize: 10
            anchors { leftMargin: 2; rightMargin: 2 }
            color: "#eeeeee"
            //text: ""
            selectByMouse: true
            onEditingFinished: labeledInput.changed(text)
        }
    }
}
