export async function getLabel(translation, previousTask: string, task) {
  var labels = await getLabels(task);
  if (previousTask) {
    var previousTaskIndex = labels.findIndex(
      (x) => x.name == previousTask.replaceAll("-", "_")
    );
  } else {
    var previousTaskIndex = -1;
  }

  var label = labels[previousTaskIndex + 1];
  if (!label) return;
  if (label.type == "flags") {
    var resultsTask: Array<{
      name: string;
      type: string;
      question?: string;
      description?: string;
      max?: string;
      min?: string;
    }> = await getFlags(translation, task);
    return { resultsTask, list: true };
  } else {
    let resultTask: {
      name: string;
      type: string;
      question?: string;
      description?: string;
      max?: string;
      min?: string;
    } = {
      name: label.name,
      type: label.type,
      ...labelText(label, translation),
    };

    return { resultsTask: [{ ...resultTask }], list: false };
  }
}

export async function getFlags(translation, task) {
  var labels = await getLabels(task);
  labels = labels.filter((x) => x.type == "flags");
  var resultsTask: Array<{
    name: string;
    type: string;
    question?: string;
    description?: string;
    max?: string;
    min?: string;
  }> = [];
  for (var i = 0; i < labels.length; i++) {
    let lbl = labels[i];
    let resultTask = {
      name: lbl.name,
      type: lbl.type,
      ...labelText(lbl, translation),
    };
    if (resultTask) {
      resultsTask.push(resultTask);
    }
  }
  return resultsTask;
}

export function labelText(label, translation) {
  var resultTask: {
    question?: string;
    description?: string;
    max?: string;
    min?: string;
  } = {};
  if (label.name == "spam") {
    resultTask.question = translation["spam.question"];
    resultTask.description = `${translation["spam.one_desc.line_1"]}\n${translation["spam.one_desc.line_2"]}`;
  } else if (label.name == "fails_task") {
    resultTask.question = translation["fails_task.question"];
    resultTask.description = `${translation["fails_task.one_desc"]}`;
  } else if (label.name == "lang_mismatch") {
    resultTask.question = `${translation["lang_mismatch"]}`;
  } else if (label.name == "not_appropriate") {
    resultTask.question = `${translation["inappropriate.one_desc"]}`;
  } else if (label.name == "pii") {
    resultTask.question = `${translation["pii"]}`;
    resultTask.description = `${translation["pii.explanation"]}`;
  } else if (label.name == "hate_speech") {
    resultTask.question = `${translation["hate_speech"]}`;
    resultTask.description = `${translation["hate_speech.explanation"]}`;
  } else if (label.name == "sexual_content") {
    resultTask.question = `${translation["sexual_content"]}`;
    resultTask.description = `${translation["sexual_content.explanation"]}`;
  } else if (label.name == "quality") {
    resultTask.max = `${translation["high_quality"]}`;
    resultTask.min = `${translation["low_quality"]}`;
  } else if (label.name == "helpfulness") {
    resultTask.max = `${translation["helpful"]}`;
    resultTask.min = `${translation["unhelpful"]}`;
  } else if (label.name == "creativity") {
    resultTask.max = `${translation["creative"]}`;
    resultTask.min = `${translation["ordinary"]}`;
  } else if (label.name == "humor") {
    resultTask.max = `${translation["humorous"]}`;
    resultTask.min = `${translation["serious"]}`;
  } else if (label.name == "toxicity") {
    resultTask.max = `${translation["polite"]}`;
    resultTask.min = `${translation["rude"]}`;
  } else if (label.name == "violence") {
    resultTask.max = `${translation["harmless"]}`;
    resultTask.min = `${translation["violent"]}`;
  }
  return resultTask;
}

export async function getLabels(task) {
  var labels = [];
  var workingLabels = [
    "spam",
    "quality",
    "lang_mismatch",
    "not_appropriate",
    "pii",
    "hate_speech",
    "sexual_content",
    "political_content",
  ];
  for (var i = 0; i < workingLabels.length; i++) {
    var type = "flags";
    if (
      workingLabels[i] == "quality" ||
      workingLabels[i] == "toxicity" ||
      workingLabels[i] == "humor" ||
      workingLabels[i] == "helpfulness" ||
      workingLabels[i] == "creativity" ||
      workingLabels[i] == "violence"
    ) {
      type = "number";
    }
    if (workingLabels[i] == "spam" || workingLabels[i] == "fails_task")
      type = "yes/no";

    if (task.valid_labels.includes(workingLabels[i])) {
      labels.push({
        name: workingLabels[i],
        type: type,
      });
    }
  }
  return labels;
}

export function formatLabel(label: string, type1?: boolean) {
  if (label == "yes") {
    return 1;
  } else if (label == "no") {
    return 0;
  } else if (label == "skip") {
    return 0;
  } else if (label == "1" && !type1) {
    return 0.0;
  } else if (label == "2") {
    return 0.25;
  } else if (label == "3") {
    return 0.5;
  } else if (label == "4") {
    return 0.75;
  } else if (label == "5") {
    return 1.0;
  } else {
    return parseInt(label);
  }
}
