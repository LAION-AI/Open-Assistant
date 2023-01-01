const RankItem = ({ username, score }) => {
  return (
    <div className="flex flex-row justify-between p-6 border-2 border-slate-100 text-left font-semibold hover:bg-sky-50">
      <div>1</div>
      <div>{username}</div>
      <div>{score}</div>
      <div>gold</div>
    </div>
  );
};

export default RankItem;
